from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.projects.models import Project
from app.projects.repository import ProjectRepository
from app.projects.schemas import ProjectCreate


class ProjectService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.projects = ProjectRepository(session)

    def create_project(self, payload: ProjectCreate, owner_id: UUID) -> Project:
        project = Project(
            project_name=payload.project_name,
            description=payload.description,
            owner_id=owner_id,
        )
        self.projects.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def list_projects(self, owner_id: UUID, limit: int, offset: int) -> list[Project]:
        return self.projects.list_for_user(owner_id=owner_id, limit=limit, offset=offset)

    def get_project_for_user(self, project_id: UUID, owner_id: UUID) -> Project:
        project = self.projects.get_by_id(project_id)
        if project is None or project.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project
