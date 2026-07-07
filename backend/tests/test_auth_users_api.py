
































from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from tests.helpers import TEST_PASSWORD, login_headers, register_user


def test_register_login_and_read_current_user(client: TestClient) -> None:
    user = register_user(client, email="api-owner@example.com")

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": user["email"], "password": TEST_PASSWORD},
    )

    assert login_response.status_code == 200
    token_payload = login_response.json()
    assert token_payload["token_type"] == "bearer"
    assert token_payload["access_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token_payload['access_token']}"},
    )

    assert response.status_code == 200
    me_payload = response.json()
    assert me_payload["id"] == user["id"]
    assert me_payload["email"] == "api-owner@example.com"
    assert "hashed_password" not in me_payload


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    register_user(client, email="duplicate@example.com")

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "DUPLICATE@example.com",
            "full_name": "Duplicate User",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 409


def test_login_rejects_invalid_password(client: TestClient) -> None:
    register_user(client, email="bad-login@example.com")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "bad-login@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_private_user_endpoint_requires_token(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_list_users_requires_auth_and_supports_pagination(
    client: TestClient,
    registered_user: dict[str, Any],
) -> None:
    register_user(client, email="listed@example.com")
    headers = login_headers(client, registered_user["email"])

    response = client.get("/api/v1/users?limit=1&offset=0", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert "hashed_password" not in payload[0]


def test_list_users_rejects_anonymous_access(client: TestClient) -> None:
    response = client.get("/api/v1/users")

    assert response.status_code == 401
