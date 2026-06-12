from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GenForge"
    app_env: str = "development"
    secret_key: str = Field(default="change-me-in-production", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+psycopg://genforge:genforge@localhost:5432/genforge"
    redis_url: str = "redis://localhost:6379/0"
    storage_dir: str = "storage/uploads"
    backend_cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    celery_task_always_eager: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GENFORGE_",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
