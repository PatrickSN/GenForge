from __future__ import annotations

from typing import Protocol
from uuid import UUID


class GenomicSelectionEngine(Protocol):
    def rank_candidates(self, project_id: UUID) -> None:
        """Future genomic selection entrypoint."""
