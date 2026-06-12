from __future__ import annotations

from pathlib import Path
from typing import Protocol


class VariantAnnotator(Protocol):
    def annotate(self, input_vcf: Path, output_vcf: Path, genome: str) -> Path:
        """Annotate a VCF file. SnpEff/Nextflow implementations will plug in here."""
