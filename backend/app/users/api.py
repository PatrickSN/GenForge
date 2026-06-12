from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser
from app.core.database import get_session
from app.users.schemas import UserRead
from app.users.service import UserService

router = APIRouter()


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.get("", response_model=list[UserRead])
def list_users(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[UserRead]:
    _ = current_user
    users = UserService(session).list_users(limit=limit, offset=offset)
    return [UserRead.model_validate(user) for user in users]
