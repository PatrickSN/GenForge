from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser
from app.core.database import get_session
from app.core.pagination import Page
from app.variants.schemas import (
    UploadResponse,
    VariantFileRead,
    VariantFilter,
    VariantProcessingJobRead,
    VariantRead,
)
from app.variants.service import VariantService

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_vcf(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    project_id: Annotated[UUID, Query()],
    file: Annotated[UploadFile, File(description="VCF or VCF.GZ file")],
) -> UploadResponse:
    variant_file, job = await VariantService(session).upload_vcf(
        project_id=project_id,
        uploaded_by_id=current_user.id,
        upload=file,
    )
    return UploadResponse(
        file=VariantFileRead.model_validate(variant_file),
        job=VariantProcessingJobRead.model_validate(job),
    )


@router.get("", response_model=Page[VariantRead])
def list_variants(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    project_id: Annotated[UUID, Query()],
    chromosome: Annotated[str | None, Query(max_length=64)] = None,
    gene_id: Annotated[str | None, Query(max_length=255)] = None,
    impact: Annotated[str | None, Query(max_length=64)] = None,
    start: Annotated[int | None, Query(ge=1)] = None,
    end: Annotated[int | None, Query(ge=1)] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[VariantRead]:
    filters = VariantFilter(
        project_id=project_id,
        chromosome=chromosome,
        gene_id=gene_id,
        impact=impact,
        start=start,
        end=end,
    )
    items, total = VariantService(session).list_variants(
        filters,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[VariantRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )
