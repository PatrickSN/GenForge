from __future__ import annotations

from app.core.database import build_database_connection_error_message, mask_database_url


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
