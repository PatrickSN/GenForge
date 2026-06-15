from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.projects.models import Project
    from app.samples.models import Sample
    from app.users.models import User

class Gene(Base):
    __tablename__ = "genes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gene_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    chromosome: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    variants: Mapped[list[Variant]] = relationship(back_populates="gene")


class VariantFile(Base):
    __tablename__ = "variant_files"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="uploaded")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project: Mapped[Project] = relationship(back_populates="files")
    uploaded_by: Mapped[User] = relationship(back_populates="uploads")
    processing_jobs: Mapped[list[VariantProcessingJob]] = relationship(back_populates="file")
    variants: Mapped[list[Variant]] = relationship(back_populates="source_file")


class VariantProcessingJob(Base):
    __tablename__ = "variant_processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("variant_files.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="queued")
    tool: Mapped[str] = mapped_column(String(64), nullable=False, default="vcf-ingest")
    variants_inserted: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    log: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    file: Mapped[VariantFile] = relationship(back_populates="processing_jobs")


class Variant(Base):
    __tablename__ = "variants"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    sample_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("samples.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    chromosome: Mapped[str] = mapped_column(String(64), nullable=False)
    position: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reference: Mapped[str] = mapped_column(Text, nullable=False)
    alternative: Mapped[str] = mapped_column(Text, nullable=False)
    impact: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    gene_id: Mapped[str | None] = mapped_column(
        String(255),
        ForeignKey("genes.gene_id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("variant_files.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project: Mapped[Project] = relationship(back_populates="variants")
    sample: Mapped[Sample | None] = relationship(back_populates="variants")
    gene: Mapped[Gene | None] = relationship(back_populates="variants")
    source_file: Mapped[VariantFile | None] = relationship(back_populates="variants")
