from __future__ import annotations

import gzip
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class VariantIngestRecord:
    chromosome: str
    position: int
    reference: str
    alternative: str
    impact: str | None
    gene_id: str | None
    sample_name: str | None


def parse_vcf_file(path: str | Path) -> Iterator[VariantIngestRecord]:
    file_path = Path(path)
    opener = gzip.open if file_path.suffix == ".gz" else open
    sample_names: list[str] = []

    with opener(file_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                columns = line.strip().split("\t")
                sample_names = columns[9:]
                continue
            if not line.strip():
                continue

            columns = line.rstrip("\n").split("\t")
            if len(columns) < 8:
                continue

            chromosome, position, _record_id, reference, alternatives, _qual, _filter, info = (
                columns[:8]
            )
            impact, gene_id = _extract_snpeff_annotation(info)
            sample_name = sample_names[0] if len(sample_names) == 1 else None
            for alternative in alternatives.split(","):
                yield VariantIngestRecord(
                    chromosome=chromosome,
                    position=int(position),
                    reference=reference,
                    alternative=alternative,
                    impact=impact,
                    gene_id=gene_id,
                    sample_name=sample_name,
                )


def _extract_snpeff_annotation(info: str) -> tuple[str | None, str | None]:
    fields = dict(
        item.split("=", 1)
        for item in info.split(";")
        if "=" in item and not item.startswith("ANN=")
    )
    if "GENE" in fields:
        return fields.get("IMPACT"), fields["GENE"]

    ann = next(
        (item.removeprefix("ANN=") for item in info.split(";") if item.startswith("ANN=")), None
    )
    if ann is None:
        return None, None

    first_annotation = ann.split(",", 1)[0].split("|")
    impact = first_annotation[2] if len(first_annotation) > 2 and first_annotation[2] else None
    gene_id = first_annotation[4] if len(first_annotation) > 4 and first_annotation[4] else None
    return impact, gene_id
