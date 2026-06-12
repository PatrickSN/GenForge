from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.samples.models import Sample
from app.variants.models import Gene, Variant, VariantFile, VariantProcessingJob
from app.variants.parser import VariantIngestRecord
from app.variants.schemas import VariantFilter


class VariantRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_file(self, file: VariantFile) -> None:
        self.session.add(file)

    def add_job(self, job: VariantProcessingJob) -> None:
        self.session.add(job)

    def get_file(self, file_id: UUID) -> VariantFile | None:
        return self.session.get(VariantFile, file_id)

    def get_job(self, job_id: UUID) -> VariantProcessingJob | None:
        return self.session.get(VariantProcessingJob, job_id)

    def list_variants(self, filters: VariantFilter, limit: int, offset: int) -> tuple[list[Variant], int]:
        stmt = self._filtered_statement(filters)
        total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items_stmt = stmt.order_by(Variant.chromosome, Variant.position).limit(limit).offset(offset)
        return list(self.session.scalars(items_stmt)), total

    def mark_job_running(self, job: VariantProcessingJob) -> None:
        job.status = "running"
        job.started_at = datetime.now(UTC)

    def mark_job_finished(self, job: VariantProcessingJob, inserted: int) -> None:
        job.status = "finished"
        job.finished_at = datetime.now(UTC)
        job.variants_inserted = inserted
        job.file.status = "processed"

    def mark_job_failed(self, job: VariantProcessingJob, message: str) -> None:
        job.status = "failed"
        job.log = message[:8000]
        job.finished_at = datetime.now(UTC)
        job.file.status = "failed"

    def insert_records(
        self,
        project_id: UUID,
        source_file_id: UUID,
        records: Iterable[VariantIngestRecord],
    ) -> int:
        inserted = 0
        batch: list[VariantIngestRecord] = []
        for record in records:
            batch.append(record)
            if len(batch) >= 5000:
                inserted += self._insert_batch(project_id, source_file_id, batch)
                batch.clear()
        if batch:
            inserted += self._insert_batch(project_id, source_file_id, batch)
        return inserted

    def _filtered_statement(self, filters: VariantFilter) -> Select[tuple[Variant]]:
        stmt = select(Variant).where(Variant.project_id == filters.project_id)
        if filters.chromosome:
            stmt = stmt.where(Variant.chromosome == filters.chromosome)
        if filters.gene_id:
            stmt = stmt.where(Variant.gene_id == filters.gene_id)
        if filters.impact:
            stmt = stmt.where(Variant.impact == filters.impact)
        if filters.start is not None:
            stmt = stmt.where(Variant.position >= filters.start)
        if filters.end is not None:
            stmt = stmt.where(Variant.position <= filters.end)
        return stmt

    def _insert_batch(
        self,
        project_id: UUID,
        source_file_id: UUID,
        batch: list[VariantIngestRecord],
    ) -> int:
        gene_ids = {record.gene_id for record in batch if record.gene_id}
        if gene_ids:
            existing_gene_ids = set(
                self.session.scalars(select(Gene.gene_id).where(Gene.gene_id.in_(gene_ids)))
            )
            for gene_id in gene_ids - existing_gene_ids:
                chromosome = next(record.chromosome for record in batch if record.gene_id == gene_id)
                self.session.add(Gene(gene_id=gene_id, chromosome=chromosome))

        sample_names = {record.sample_name for record in batch if record.sample_name}
        sample_by_name: dict[str, Sample] = {}
        if sample_names:
            existing_samples = self.session.scalars(
                select(Sample).where(
                    Sample.project_id == project_id,
                    Sample.sample_name.in_(sample_names),
                )
            )
            sample_by_name = {sample.sample_name: sample for sample in existing_samples}
            for sample_name in sample_names - set(sample_by_name):
                sample = Sample(project_id=project_id, sample_name=sample_name)
                self.session.add(sample)
                self.session.flush()
                sample_by_name[sample_name] = sample

        variants = [
            Variant(
                project_id=project_id,
                sample_id=sample_by_name[record.sample_name].id
                if record.sample_name and record.sample_name in sample_by_name
                else None,
                chromosome=record.chromosome,
                position=record.position,
                reference=record.reference,
                alternative=record.alternative,
                impact=record.impact,
                gene_id=record.gene_id,
                source_file_id=source_file_id,
            )
            for record in batch
        ]
        self.session.add_all(variants)
        self.session.commit()
        return len(variants)
