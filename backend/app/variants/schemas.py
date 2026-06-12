from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GeneRead(BaseModel):
    id: UUID
    gene_id: str
    chromosome: str

    model_config = ConfigDict(from_attributes=True)


class VariantRead(BaseModel):
    id: UUID
    project_id: UUID
    sample_id: UUID | None
    chromosome: str
    position: int
    reference: str
    alternative: str
    impact: str | None
    gene_id: str | None
    source_file_id: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VariantFilter(BaseModel):
    project_id: UUID
    chromosome: str | None = Field(default=None, max_length=64)
    gene_id: str | None = Field(default=None, max_length=255)
    impact: str | None = Field(default=None, max_length=64)
    start: int | None = Field(default=None, ge=1)
    end: int | None = Field(default=None, ge=1)


class VariantFileRead(BaseModel):
    id: UUID
    project_id: UUID
    original_filename: str
    storage_path: str
    size_bytes: int
    checksum_sha256: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VariantProcessingJobRead(BaseModel):
    id: UUID
    file_id: UUID
    status: str
    tool: str
    variants_inserted: int
    log: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    file: VariantFileRead
    job: VariantProcessingJobRead
