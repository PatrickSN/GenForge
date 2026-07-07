from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

TEST_PASSWORD = "genforge123"


def register_user(
    client: TestClient,
    email: str = "owner@example.com",
    full_name: str = "GenForge Owner",
    password: str = TEST_PASSWORD,
) -> dict[str, Any]:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": full_name, "password": password},
    )
    assert response.status_code == 201
    return response.json()


def login_headers(
    client: TestClient,
    email: str = "owner@example.com",
    password: str = TEST_PASSWORD,
) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    payload = response.json()
    return {"Authorization": f"Bearer {payload['access_token']}"}


def create_project(
    client: TestClient,
    headers: dict[str, str],
    name: str = "Soy VCF",
    description: str = "Phase 1 project",
) -> dict[str, Any]:
    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"project_name": name, "description": description},
    )
    assert response.status_code == 201
    return response.json()
