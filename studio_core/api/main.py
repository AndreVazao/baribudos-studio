from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from studio_core.api.routes.diagnostics import router as diagnostics_router
from studio_core.api.routes.health import router as health_router
from studio_core.api.routes.projects import router as projects_router
from studio_core.api.routes.users import ensure_default_owner, router as users_router
from studio_core.core.config import APP_CONFIG
from studio_core.core.storage import ensure_storage_structure


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_storage_structure()
    ensure_default_owner()
    yield


app = FastAPI(
    title=APP_CONFIG.app_name,
    version=APP_CONFIG.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(diagnostics_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(projects_router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {
        "ok": True,
        "app_name": APP_CONFIG.app_name,
        "version": APP_CONFIG.app_version,
        "docs": "/docs",
        "health": "/api/health"
}
