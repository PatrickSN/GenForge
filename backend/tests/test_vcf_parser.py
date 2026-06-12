from __future__ import annotations

from pathlib import Path

from app.variants.parser import parse_vcf_file


def test_parse_vcf_with_snpeff_ann(tmp_path: Path) -> None:
    vcf = tmp_path / "sample.vcf"
    vcf.write_text(
        "\n".join(
            [
                "##fileformat=VCFv4.2",
                "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tEMS_001",
                "Chr1\t42\t.\tG\tA\t.\tPASS\tANN=A|missense_variant|MODERATE|ABC1|Gene001|transcript|T1|protein_coding|1/1|c.1G>A|p.Gly1Ser\tGT\t0/1",
            ]
        ),
        encoding="utf-8",
    )

    records = list(parse_vcf_file(vcf))

    assert len(records) == 1
    assert records[0].chromosome == "Chr1"
    assert records[0].position == 42
    assert records[0].reference == "G"
    assert records[0].alternative == "A"
    assert records[0].impact == "MODERATE"
    assert records[0].gene_id == "Gene001"
    assert records[0].sample_name == "EMS_001"
