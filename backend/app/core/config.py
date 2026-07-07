from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Self

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://200.235.143.10:5173",
]


class Settings(BaseSettings):
    app_name: str = "GenForge"
    app_env: str = Field(
        default="development",
        validation_alias=AliasChoices("GENFORGE_APP_ENV", "APP_ENV"),
    )
    secret_key: str = Field(
        default="change-me-in-production",
        validation_alias=AliasChoices("GENFORGE_SECRET_KEY", "SECRET_KEY"),
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(
        default=60,
        validation_alias=AliasChoices(
            "GENFORGE_ACCESS_TOKEN_EXPIRE_MINUTES",
            "ACCESS_TOKEN_EXPIRE_MINUTES",
        ),
    )
    database_url: str = Field(
        default="postgresql+psycopg://genforge:genforge@localhost:5432/genforge",
        validation_alias=AliasChoices("GENFORGE_DATABASE_URL", "DATABASE_URL"),
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("GENFORGE_REDIS_URL", "REDIS_URL"),
    )
    storage_dir: str = Field(
        default="storage_data",
        validation_alias=AliasChoices("GENFORGE_STORAGE_DIR", "STORAGE_DIR"),
    )
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("GENFORGE_LOG_LEVEL", "LOG_LEVEL"),
    )
    backend_cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: list(DEFAULT_CORS_ORIGINS),
        validation_alias=AliasChoices(
            "GENFORGE_BACKEND_CORS_ORIGINS",
            "GENFORGE_CORS_ORIGINS",
            "CORS_ORIGINS",
        ),
    )
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
            origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        else:
            origins = [origin.strip() for origin in value if origin.strip()]
        if not origins:
            raise ValueError(
                "CORS_ORIGINS must include at least one origin. "
                "Set CORS_ORIGINS or GENFORGE_BACKEND_CORS_ORIGINS in backend/.env."
            )
        return origins

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        database_url = value.strip()
        if not database_url:
            raise ValueError(
                "DATABASE_URL must be configured. "
                "Set DATABASE_URL or GENFORGE_DATABASE_URL in backend/.env."
            )
        return database_url

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        secret_key = value.strip()
        if len(secret_key) < 16:
            raise ValueError(
                "SECRET_KEY must contain at least 16 characters. "
                "Set SECRET_KEY or GENFORGE_SECRET_KEY in backend/.env."
            )
        return secret_key

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        log_level = value.strip().upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if log_level not in allowed:
            raise ValueError("LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR or CRITICAL.")
        return log_level

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Self:
        uses_production_env = self.app_env.lower() in {"prod", "production"}
        uses_default_secret = self.secret_key == "change-me-in-production"
        if uses_production_env and uses_default_secret:
            raise ValueError(
                "SECRET_KEY must be changed when APP_ENV or GENFORGE_APP_ENV is production."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
