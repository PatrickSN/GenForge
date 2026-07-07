from __future__ import annotations

import logging
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.auth.api import router as auth_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.projects.api import router as projects_router
from app.users.api import router as users_router
from app.variants.api import router as variants_router

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="GenForge API",
    description="API para bioinformatica vegetal, anotacao e consulta de variantes genomicas.",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_logger = logging.getLogger("genforge.requests")
    started_at = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        request_logger.exception(
            "request_failed method=%s path=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    request_logger.info(
        "request_completed method=%s path=%s status_code=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "name": "GenForge API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(projects_router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(variants_router, prefix="/api/v1/variants", tags=["variants"])
