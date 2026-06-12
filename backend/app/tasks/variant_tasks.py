from __future__ import annotations

from uuid import UUID

from app.core.database import SessionLocal
from app.tasks.celery_app import celery_app
from app.variants.parser import parse_vcf_file
from app.variants.repository import VariantRepository


@celery_app.task(name="variants.process_variant_file")
def process_variant_file(job_id: str) -> dict[str, int | str]:
    with SessionLocal() as session:
        repository = VariantRepository(session)
        job = repository.get_job(UUID(job_id))
        if job is None:
            return {"status": "not_found", "variants_inserted": 0}

        try:
            repository.mark_job_running(job)
            session.commit()
            records = parse_vcf_file(job.file.storage_path)
            inserted = repository.insert_records(
                project_id=job.file.project_id,
                source_file_id=job.file.id,
                records=records,
            )
            repository.mark_job_finished(job, inserted=inserted)
            session.commit()
            return {"status": "finished", "variants_inserted": inserted}
        except Exception as exc:
            session.rollback()
            job = repository.get_job(UUID(job_id))
            if job is not None:
                repository.mark_job_failed(job, message=str(exc))
                session.commit()
            raise
