from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "GenForge API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


def test_cors_allows_server_frontend_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/health",
        headers={
            "Origin": "http://200.235.143.10:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://200.235.143.10:5173"
