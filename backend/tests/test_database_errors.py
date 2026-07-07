from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError

from app.core import database
from app.core.database import (
    build_database_connection_error_message,
    mask_database_url,
)


def test_mask_database_url_hides_password() -> None:
    masked = mask_database_url(
        "postgresql+psycopg://genforge:server-secret@localhost:5432/genforge"
    )

    assert "server-secret" not in masked
    assert "***" in masked


def test_database_connection_error_message_hides_password() -> None:
    message = build_database_connection_error_message(
        "postgresql+psycopg://genforge:server-secret@localhost:5432/genforge",
        RuntimeError("password server-secret failed"),
        "Alembic migrations",
    )

    assert "server-secret" not in message
    assert "DATABASE_URL" in message
    assert "backend/.env" in message
    assert "Alembic migrations" in message


def test_get_session_translates_sqlalchemy_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySession:
        rolled_back = False
        closed = False

        def rollback(self) -> None:
            self.rolled_back = True

        def close(self) -> None:
            self.closed = True

    session = DummySession()
    monkeypatch.setattr(database, "SessionLocal", lambda: session)

    generator = database.get_session()
    assert next(generator) is session

    with pytest.raises(HTTPException) as exc_info:
        generator.throw(
            OperationalError(
                "select 1",
                {},
                RuntimeError("password server-secret failed"),
            )
        )

    assert exc_info.value.status_code == 503
    assert "backend/.env" in str(exc_info.value.detail)
    assert "server-secret" not in str(exc_info.value.detail)
    assert session.rolled_back is True
    assert session.closed is True
