from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    project_name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=5000)


class ProjectRead(BaseModel):
    id: UUID
    project_name: str
    description: str | None
    owner_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
