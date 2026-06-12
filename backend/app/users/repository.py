from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, user: User) -> None:
        self.session.add(user)

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        return self.session.scalar(stmt)

    def list(self, limit: int = 100, offset: int = 0) -> list[User]:
        stmt = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        return list(self.session.scalars(stmt))
