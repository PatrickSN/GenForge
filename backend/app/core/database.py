from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=naming_convention)


def mask_database_url(database_url: str) -> str:
    try:
        return make_url(database_url).render_as_string(hide_password=True)
    except Exception:
        return "<invalid DATABASE_URL>"


def _sanitize_database_error(error: BaseException, database_url: str) -> str:
    text = str(error).strip() or error.__class__.__name__
    try:
        password = make_url(database_url).password
    except Exception:
        password = None
    if password:
        text = text.replace(password, "***")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:6])


def build_database_connection_error_message(
    database_url: str,
    error: BaseException,
    action: str,
) -> str:
    return "\n".join(
        [
            f"Could not connect to PostgreSQL while running {action}.",
            f"DATABASE_URL in use: {mask_database_url(database_url)}",
            "Verify DATABASE_URL or GENFORGE_DATABASE_URL in backend/.env.",
            "Check the database host, port, name, user and password on the server.",
            "Do not commit real database credentials.",
            f"Database error: {_sanitize_database_error(error, database_url)}",
        ]
    )


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    try:
        return create_engine(settings.database_url, pool_pre_ping=True)
    except SQLAlchemyError as exc:
        raise RuntimeError(
            build_database_connection_error_message(
                settings.database_url,
                exc,
                "database engine startup",
            )
        ) from exc


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(),
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


def SessionLocal() -> Session:
    return get_session_factory()()


def get_session() -> Generator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
