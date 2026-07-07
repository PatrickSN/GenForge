from __future__ import annotations

from app.core.config import Settings


def test_settings_accept_server_env_names(monkeypatch) -> None:
    for name in (
        "GENFORGE_DATABASE_URL",
        "GENFORGE_SECRET_KEY",
        "GENFORGE_BACKEND_CORS_ORIGINS",
        "GENFORGE_CORS_ORIGINS",
    ):
        monkeypatch.delenv(name, raising=False)

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://genforge:genforge@db.example:5432/genforge",
    )
    monkeypatch.setenv("SECRET_KEY", "server-test-secret-key")
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://200.235.143.10:5173",
    )
    monkeypatch.setenv("LOG_LEVEL", "debug")

    settings = Settings(_env_file=None)

    assert settings.database_url == "postgresql+psycopg://genforge:genforge@db.example:5432/genforge"
    assert settings.secret_key == "server-test-secret-key"
    assert settings.backend_cors_origins == [
        "http://localhost:5173",
        "http://200.235.143.10:5173",
    ]
    assert settings.log_level == "DEBUG"
