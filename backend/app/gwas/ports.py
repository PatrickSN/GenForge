from __future__ import annotations

from typing import Protocol
from uuid import UUID


class GwasRunner(Protocol):
    def run_association(self, project_id: UUID) -> None:
        """Future GWAS entrypoint."""
