from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.variants.parser import parse_vcf_file
from app.variants.repository import VariantRepository
from tests.helpers import login_headers, register_user


def upload_minimal_vcf(
    client: TestClient,
    headers: dict[str, str],
    project_id: str,
    content: bytes,
) -> dict[str, Any]:
    response = client.post(
        f"/api/v1/variants/upload?project_id={project_id}",
        headers=headers,
        files={"file": ("sample.vcf", content, "text/plain")},
    )
    assert response.status_code == 202
    return response.json()


def test_vcf_upload_exposes_file_and_job_status(
    client: TestClient,
    auth_headers: dict[str, str],
    project: dict[str, Any],
    minimal_vcf_bytes: bytes,
    celery_delay_calls: list[str],
) -> None:
    register_user(client, email="viewer@example.com")
    other_headers = login_headers(client, "viewer@example.com")
    project_id = project["id"]

    upload_payload = upload_minimal_vcf(client, auth_headers, project_id, minimal_vcf_bytes)
    file_payload = upload_payload["file"]
    job_payload = upload_payload["job"]

    assert file_payload["status"] == "uploaded"
    assert job_payload["status"] == "queued"
    assert celery_delay_calls == [job_payload["id"]]

    storage_path = Path(file_payload["storage_path"])
    assert storage_path.exists()
    assert storage_path.parent.name == project_id
    assert storage_path.parent.parent.name == "projects"

    response = client.get(
        f"/api/v1/variants/files?project_id={project_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    files_page = response.json()
    assert files_page["total"] == 1
    assert files_page["items"][0]["id"] == file_payload["id"]
    assert files_page["items"][0]["updated_at"]

    response = client.get(
        f"/api/v1/variants/jobs?project_id={project_id}&status=queued",
        headers=auth_headers,
    )
    assert response.status_code == 200
    jobs_page = response.json()
    assert jobs_page["total"] == 1
    assert jobs_page["items"][0]["id"] == job_payload["id"]

    response = client.get(f"/api/v1/variants/jobs/{job_payload['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == job_payload["id"]

    response = client.get(
        f"/api/v1/variants/files?project_id={project_id}",
        headers=other_headers,
    )
    assert response.status_code == 404


def test_vcf_upload_rejects_invalid_extension(
    client: TestClient,
    auth_headers: dict[str, str],
    project: dict[str, Any],
) -> None:
    response = client.post(
        f"/api/v1/variants/upload?project_id={project['id']}",
        headers=auth_headers,
        files={"file": ("sample.txt", b"not a vcf", "text/plain")},
    )

    assert response.status_code == 400


def test_project_delete_cascades_uploaded_files_and_jobs(
    client: TestClient,
    auth_headers: dict[str, str],
    project: dict[str, Any],
    minimal_vcf_bytes: bytes,
) -> None:
    upload_minimal_vcf(client, auth_headers, project["id"], minimal_vcf_bytes)

    response = client.delete(f"/api/v1/projects/{project['id']}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(
        f"/api/v1/variants/files?project_id={project['id']}",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_list_variants_is_paginated_filterable_and_scoped_to_owner(
    client: TestClient,
    auth_headers: dict[str, str],
    project: dict[str, Any],
    minimal_vcf_bytes: bytes,
    db_session: Session,
) -> None:
    upload_payload = upload_minimal_vcf(client, auth_headers, project["id"], minimal_vcf_bytes)
    file_payload = upload_payload["file"]

    inserted = VariantRepository(db_session).insert_records(
        project_id=UUID(project["id"]),
        source_file_id=UUID(file_payload["id"]),
        records=parse_vcf_file(Path(file_payload["storage_path"])),
    )
    assert inserted == 1

    response = client.get(
        f"/api/v1/variants?project_id={project['id']}&limit=25&offset=0",
        headers=auth_headers,
    )
    assert response.status_code == 200
    page = response.json()
    assert page["total"] == 1
    assert page["items"][0]["chromosome"] == "Chr1"
    assert page["items"][0]["position"] == 42
    assert page["items"][0]["gene_id"] == "Gene001"
    assert page["items"][0]["impact"] == "MODERATE"

    response = client.get(
        (
            f"/api/v1/variants?project_id={project['id']}"
            "&chromosome=Chr1&gene_id=Gene001&impact=MODERATE&start=40&end=50"
        ),
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = client.get(
        f"/api/v1/variants?project_id={project['id']}&chromosome=Chr9",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0

    register_user(client, email="variant-viewer@example.com")
    other_headers = login_headers(client, "variant-viewer@example.com")
    response = client.get(
        f"/api/v1/variants?project_id={project['id']}",
        headers=other_headers,
    )
    assert response.status_code == 404


def test_variant_endpoints_require_authentication(
    client: TestClient,
    project: dict[str, Any],
) -> None:
    response = client.get(f"/api/v1/variants?project_id={project['id']}")

    assert response.status_code == 401
