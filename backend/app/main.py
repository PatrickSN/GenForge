from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.api import router as auth_router
from app.core.config import get_settings
from app.projects.api import router as projects_router
from app.users.api import router as users_router
from app.variants.api import router as variants_router

settings = get_settings()

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
