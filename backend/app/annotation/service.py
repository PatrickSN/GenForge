from __future__ import annotations

from pathlib import Path


class AnnotationService:
    def request_snpeff_annotation(self, input_vcf: Path, genome: str) -> None:
        _ = (input_vcf, genome)
        raise NotImplementedError("SnpEff annotation pipeline is planned for a future iteration.")
