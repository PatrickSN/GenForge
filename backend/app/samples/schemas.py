from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SampleCreate(BaseModel):
    sample_name: str = Field(min_length=1, max_length=255)
    project_id: UUID


class SampleRead(BaseModel):
    id: UUID
    sample_name: str
    project_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
