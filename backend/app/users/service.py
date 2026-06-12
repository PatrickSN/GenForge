from __future__ import annotations

from sqlalchemy.orm import Session

from app.users.models import User
from app.users.repository import UserRepository


class UserService:
    def __init__(self, session: Session) -> None:
        self.users = UserRepository(session)

    def list_users(self, limit: int, offset: int) -> list[User]:
        return self.users.list(limit=limit, offset=offset)
