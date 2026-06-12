from __future__ import annotations

from pathlib import Path
from typing import Protocol
from uuid import UUID


class ReportGenerator(Protocol):
    def build_variant_report(self, project_id: UUID, output_dir: Path) -> Path:
        """Generate a project-level report artifact."""
