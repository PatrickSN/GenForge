from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.projects.models import Project


class ProjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, project: Project) -> None:
        self.session.add(project)

    def get_by_id(self, project_id: UUID) -> Project | None:
        return self.session.get(Project, project_id)

    def list_for_user(self, owner_id: UUID, limit: int, offset: int) -> list[Project]:
        stmt = (
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(stmt))

    def delete(self, project: Project) -> None:
        self.session.delete(project)
