from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.core.security import create_access_token, hash_password, verify_password
from app.users.models import User
from app.users.repository import UserRepository


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def register(self, payload: RegisterRequest) -> User:
        existing = self.users.get_by_email(payload.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )
        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
        self.users.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
        return TokenResponse(access_token=create_access_token(str(user.id)))
