from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.samples.models import Sample
from app.samples.repository import SampleRepository


class SampleService:
    def __init__(self, session: Session) -> None:
        self.samples = SampleRepository(session)

    def get_or_create_sample(self, project_id: UUID, sample_name: str) -> Sample:
        return self.samples.get_or_create(project_id=project_id, sample_name=sample_name)
