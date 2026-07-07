from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.projects.repository import ProjectRepository
from app.storage.local import LocalObjectStorage
from app.variants.models import VariantFile, VariantProcessingJob
from app.variants.repository import VariantRepository
from app.variants.schemas import VariantFilter


class VariantService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.variants = VariantRepository(session)
        self.projects = ProjectRepository(session)
        self.storage = LocalObjectStorage()

    async def upload_vcf(
        self,
        project_id: UUID,
        uploaded_by_id: UUID,
        upload: UploadFile,
    ) -> tuple[VariantFile, VariantProcessingJob]:
        if not (upload.filename or "").lower().endswith((".vcf", ".vcf.gz")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .vcf and .vcf.gz files are accepted",
            )
        project = self.projects.get_by_id(project_id)
        if project is None or project.owner_id != uploaded_by_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        storage_path, size_bytes, checksum = await self.storage.save_upload(
            upload,
            namespace=f"projects/{project_id}",
        )
        variant_file = VariantFile(
            project_id=project_id,
            uploaded_by_id=uploaded_by_id,
            original_filename=upload.filename or "variants.vcf",
            storage_path=str(storage_path),
            size_bytes=size_bytes,
            checksum_sha256=checksum,
            status="uploaded",
        )
        self.variants.add_file(variant_file)
        self.session.flush()
        job = VariantProcessingJob(file_id=variant_file.id, status="queued", tool="vcf-ingest")
        self.variants.add_job(job)
        self.session.commit()
        self.session.refresh(variant_file)
        self.session.refresh(job)

        from app.tasks.variant_tasks import process_variant_file

        process_variant_file.delay(str(job.id))
        return variant_file, job

    def list_variants(self, filters: VariantFilter, user_id: UUID, limit: int, offset: int):
        project = self.projects.get_by_id(filters.project_id)
        if project is None or project.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return self.variants.list_variants(filters, limit=limit, offset=offset)

    def list_files(self, project_id: UUID, user_id: UUID, limit: int, offset: int):
        project = self.projects.get_by_id(project_id)
        if project is None or project.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return self.variants.list_files_for_project(project_id, limit=limit, offset=offset)

    def list_jobs(
        self,
        project_id: UUID,
        user_id: UUID,
        limit: int,
        offset: int,
        status_filter: str | None = None,
    ):
        project = self.projects.get_by_id(project_id)
        if project is None or project.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return self.variants.list_jobs_for_project(
            project_id,
            limit=limit,
            offset=offset,
            status=status_filter,
        )

    def get_job(self, job_id: UUID, user_id: UUID) -> VariantProcessingJob:
        job = self.variants.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        project = self.projects.get_by_id(job.file.project_id)
        if project is None or project.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        return job
