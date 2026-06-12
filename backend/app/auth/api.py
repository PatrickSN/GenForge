from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.auth.service import AuthService
from app.core.database import get_session
from app.users.schemas import UserRead

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: RegisterRequest, session: Annotated[Session, Depends(get_session)]) -> UserRead:
    user = AuthService(session).register(payload)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Annotated[Session, Depends(get_session)]) -> TokenResponse:
    return AuthService(session).login(payload)
