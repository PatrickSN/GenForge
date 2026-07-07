from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.database import Base, get_session
from app.main import app
from tests.helpers import create_project, login_headers, register_user


@pytest.fixture()
def test_session_factory(
    tmp_path: Path,
) -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'genforge-test.db'}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)

    try:
        yield factory
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def db_session(test_session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = test_session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def celery_delay_calls(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []

    from app.tasks.variant_tasks import process_variant_file

    def fake_delay(job_id: str) -> dict[str, str]:
        calls.append(job_id)
        return {"job_id": job_id}

    monkeypatch.setattr(process_variant_file, "delay", fake_delay)
    return calls


@pytest.fixture()
def client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    test_session_factory: sessionmaker[Session],
    celery_delay_calls: list[str],
) -> Iterator[TestClient]:
    _ = celery_delay_calls
    monkeypatch.setenv("GENFORGE_STORAGE_DIR", str(tmp_path / "storage"))
    monkeypatch.setenv("GENFORGE_SECRET_KEY", "test-secret-key-for-genforge")
    monkeypatch.setenv("GENFORGE_APP_ENV", "test")
    get_settings.cache_clear()

    def override_get_session() -> Iterator[Session]:
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()


@pytest.fixture()
def minimal_vcf_bytes() -> bytes:
    return (
        b"##fileformat=VCFv4.2\n"
        b"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tEMS_001\n"
        b"Chr1\t42\t.\tG\tA\t.\tPASS\t"
        b"ANN=A|missense_variant|MODERATE|ABC1|Gene001|transcript|T1|protein_coding|"
        b"1/1|c.1G>A|p.Gly1Ser\tGT\t0/1\n"
    )


@pytest.fixture()
def registered_user(client: TestClient) -> dict[str, Any]:
    return register_user(client)


@pytest.fixture()
def auth_headers(client: TestClient, registered_user: dict[str, Any]) -> dict[str, str]:
    return login_headers(client, registered_user["email"])


@pytest.fixture()
def project(client: TestClient, auth_headers: dict[str, str]) -> dict[str, Any]:
    return create_project(client, auth_headers)
