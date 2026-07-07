from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser
from app.core.database import get_session
from app.projects.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.projects.service import ProjectService

router = APIRouter()


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(
    payload: ProjectCreate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ProjectRead:
    project = ProjectService(session).create_project(payload, owner_id=current_user.id)
    return ProjectRead.model_validate(project)


@router.get("", response_model=list[ProjectRead])
def list_projects(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ProjectRead]:
    projects = ProjectService(session).list_projects(current_user.id, limit=limit, offset=offset)
    return [ProjectRead.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ProjectRead:
    project = ProjectService(session).get_project_for_user(project_id, current_user.id)
    return ProjectRead.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> ProjectRead:
    project = ProjectService(session).update_project(project_id, payload, current_user.id)
    return ProjectRead.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    ProjectService(session).delete_project(project_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
