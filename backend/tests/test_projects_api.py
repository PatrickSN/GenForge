from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from tests.helpers import create_project, login_headers, register_user


def test_project_crud_is_scoped_to_owner(
    client: TestClient,
    auth_headers: dict[str, str],
    project: dict[str, Any],
) -> None:
    register_user(client, email="other@example.com")
    other_headers = login_headers(client, "other@example.com")
    project_id = project["id"]

    response = client.get("/api/v1/projects", headers=auth_headers)
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [project_id]

    response = client.get(f"/api/v1/projects/{project_id}", headers=other_headers)
    assert response.status_code == 404

    response = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers,
        json={"project_name": "Updated VCF"},
    )
    assert response.status_code == 200
    assert response.json()["project_name"] == "Updated VCF"
    assert response.json()["updated_at"]

    response = client.delete(f"/api/v1/projects/{project_id}", headers=other_headers)
    assert response.status_code == 404

    response = client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 404


def test_create_project_preserves_owner_scope(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    project_a = create_project(client, auth_headers, name="Project A")
    project_b = create_project(client, auth_headers, name="Project B")

    response = client.get("/api/v1/projects?limit=10&offset=0", headers=auth_headers)

    assert response.status_code == 200
    project_ids = {item["id"] for item in response.json()}
    assert project_ids == {project_a["id"], project_b["id"]}


def test_projects_require_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/projects")

    assert response.status_code == 401
