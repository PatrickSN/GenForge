from __future__ import annotations

import logging
from uuid import UUID

from app.core.database import SessionLocal
from app.tasks.celery_app import celery_app
from app.variants.parser import parse_vcf_file
from app.variants.repository import VariantRepository

logger = logging.getLogger("genforge.tasks.variants")


@celery_app.task(name="variants.process_variant_file")
def process_variant_file(job_id: str) -> dict[str, int | str]:
    with SessionLocal() as session:
        repository = VariantRepository(session)
        job = repository.get_job(UUID(job_id))
        if job is None:
            logger.warning("variant_job_not_found job_id=%s", job_id)
            return {"status": "not_found", "variants_inserted": 0}

        try:
            logger.info("variant_job_started job_id=%s file_id=%s", job_id, job.file_id)
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
            logger.info("variant_job_finished job_id=%s variants_inserted=%s", job_id, inserted)
            return {"status": "finished", "variants_inserted": inserted}
        except Exception as exc:
            session.rollback()
            job = repository.get_job(UUID(job_id))
            if job is not None:
                repository.mark_job_failed(job, message=str(exc))
                session.commit()
            logger.exception("variant_job_failed job_id=%s", job_id)
            raise
