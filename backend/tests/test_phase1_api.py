from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.database import Base, get_session
from app.main import app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("GENFORGE_STORAGE_DIR", str(tmp_path / "storage"))
    get_settings.cache_clear()

    engine = create_engine(
        f"sqlite:///{tmp_path / 'genforge-test.db'}",
        connect_args={"check_same_thread": False},
    )
    testing_session_factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_session() -> Iterator[Session]:
        session = testing_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session

    from app.tasks.variant_tasks import process_variant_file

    monkeypatch.setattr(process_variant_file, "delay", lambda job_id: {"job_id": job_id})

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        get_settings.cache_clear()


def auth_headers(client: TestClient, email: str = "owner@example.com") -> dict[str, str]:
    password = "genforge123"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "GenForge Owner", "password": password},
    )
    assert response.status_code == 201
    assert response.json()["email"] == email

    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_project(client: TestClient, headers: dict[str, str], name: str = "Soy VCF") -> dict:
    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"project_name": name, "description": "Phase 1 project"},
    )
    assert response.status_code == 201
    return response.json()


def test_project_crud_is_scoped_to_owner(client: TestClient) -> None:
    owner_headers = auth_headers(client)
    other_headers = auth_headers(client, email="other@example.com")

    project = create_project(client, owner_headers)
    project_id = project["id"]

    response = client.get("/api/v1/projects", headers=owner_headers)
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [project_id]

    response = client.get(f"/api/v1/projects/{project_id}", headers=other_headers)
    assert response.status_code == 404

    response = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=owner_headers,
        json={"project_name": "Updated VCF"},
    )
    assert response.status_code == 200
    assert response.json()["project_name"] == "Updated VCF"
    assert response.json()["updated_at"]

    response = client.delete(f"/api/v1/projects/{project_id}", headers=other_headers)
    assert response.status_code == 404

    response = client.delete(f"/api/v1/projects/{project_id}", headers=owner_headers)
    assert response.status_code == 204

    response = client.get(f"/api/v1/projects/{project_id}", headers=owner_headers)
    assert response.status_code == 404


def test_vcf_upload_exposes_file_and_job_status(client: TestClient) -> None:
    headers = auth_headers(client)
    other_headers = auth_headers(client, email="viewer@example.com")
    project = create_project(client, headers)
    project_id = project["id"]
    content = (
        b"##fileformat=VCFv4.2\n"
        b"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n"
        b"Chr1\t10\t.\tA\tG\t.\tPASS\t.\tGT\t0/1\n"
    )

    response = client.post(
        f"/api/v1/variants/upload?project_id={project_id}",
        headers=headers,
        files={"file": ("sample.vcf", content, "text/plain")},
    )
    assert response.status_code == 202
    upload_payload = response.json()
    file_payload = upload_payload["file"]
    job_payload = upload_payload["job"]
    assert file_payload["status"] == "uploaded"
    assert job_payload["status"] == "queued"
    storage_path = Path(file_payload["storage_path"])
    assert storage_path.exists()
    assert storage_path.parent.name == project_id
    assert storage_path.parent.parent.name == "projects"

    response = client.get(
        f"/api/v1/variants/files?project_id={project_id}",
        headers=headers,
    )
    assert response.status_code == 200
    files_page = response.json()
    assert files_page["total"] == 1
    assert files_page["items"][0]["id"] == file_payload["id"]
    assert files_page["items"][0]["updated_at"]

    response = client.get(
        f"/api/v1/variants/jobs?project_id={project_id}&status=queued",
        headers=headers,
    )
    assert response.status_code == 200
    jobs_page = response.json()
    assert jobs_page["total"] == 1
    assert jobs_page["items"][0]["id"] == job_payload["id"]

    response = client.get(f"/api/v1/variants/jobs/{job_payload['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == job_payload["id"]

    response = client.get(
        f"/api/v1/variants/files?project_id={project_id}",
        headers=other_headers,
    )
    assert response.status_code == 404
