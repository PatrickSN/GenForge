from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.samples.models import Sample


class SampleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create(self, project_id: UUID, sample_name: str) -> Sample:
        stmt = select(Sample).where(
            Sample.project_id == project_id,
            Sample.sample_name == sample_name,
        )
        sample = self.session.scalar(stmt)
        if sample is not None:
            return sample
        sample = Sample(project_id=project_id, sample_name=sample_name)
        self.session.add(sample)
        self.session.flush()
        return sample
