from __future__ import annotations

from typing import Protocol
from uuid import UUID


class GenomicModelTrainer(Protocol):
    def train(self, project_id: UUID) -> None:
        """Future IA/genomic prediction entrypoint."""
