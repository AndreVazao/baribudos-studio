from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from studio_core.api.routes.age_badges import router as age_badges_router
from studio_core.api.routes.audiobooks import router as audiobooks_router
from studio_core.api.routes.covers import router as covers_router
from studio_core.api.routes.diagnostics import router as diagnostics_router
from studio_core.api.routes.ebooks import router as ebooks_router
from studio_core.api.routes.factory import router as factory_router
from studio_core.api.routes.health import router as health_router
from studio_core.api.routes.illustration_assets import router as illustration_assets_router
from studio_core.api.routes.illustration_generation import router as illustration_generation_router
from studio_core.api.routes.illustration_pipeline import router as illustration_pipeline_router
from studio_core.api.routes.illustration_provider import router as illustration_provider_router
from studio_core.api.routes.illustrations import router as illustrations_router
from studio_core.api.routes.ip_branding import router as ip_branding_router
from studio_core.api.routes.ip_canons import router as ip_canons_router
from studio_core.api.routes.ip_characters import router as ip_characters_router
from studio_core.api.routes.ip_creator import router as ip_creator_router
from studio_core.api.routes.ip_metadata import router as ip_metadata_router
from studio_core.api.routes.ip_palette import router as ip_palette_router
from studio_core.api.routes.jobs import router as jobs_router
from studio_core.api.routes.production_pipeline import router as production_pipeline_router
from studio_core.api.routes.project_commercial import router as project_commercial_router
from studio_core.api.routes.project_integrity import router as project_integrity_router
from studio_core.api.routes.projects import router as projects_router
from studio_core.api.routes.publication_package import router as publication_package_router
from studio_core.api.routes.publish_readiness import router as publish_readiness_router
from studio_core.api.routes.publishing import router as publishing_router
from studio_core.api.routes.saga_loader import router as saga_loader_router
from studio_core.api.routes.saga_runtime import router as saga_runtime_router
from studio_core.api.routes.sagas import router as sagas_router
from studio_core.api.routes.settings import router as settings_router
from studio_core.api.routes.sponsors import router as sponsors_router
from studio_core.api.routes.story_layout import router as story_layout_router
from studio_core.api.routes.system_smoke import router as system_smoke_router
from studio_core.api.routes.users import ensure_default_owner, router as users_router
from studio_core.api.routes.videos import router as videos_router
from studio_core.core.config import APP_CONFIG, resolve_project_path, resolve_storage_path
from studio_core.services.bootstrap_service import bootstrap_system


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_system()
    ensure_default_owner()
    yield


app = FastAPI(
    title=APP_CONFIG.app_name,
    version=APP_CONFIG.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

public_dir = resolve_project_path("public")
storage_dir = resolve_storage_path()

if public_dir.exists():
    app.mount("/public", StaticFiles(directory=str(public_dir)), name="public")

if storage_dir.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_dir)), name="storage")

app.include_router(health_router, prefix="/api")
app.include_router(diagnostics_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(project_commercial_router, prefix="/api")
app.include_router(project_integrity_router, prefix="/api")
app.include_router(publication_package_router, prefix="/api")
app.include_router(publish_readiness_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(sagas_router, prefix="/api")
app.include_router(sponsors_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(factory_router, prefix="/api")
app.include_router(production_pipeline_router, prefix="/api")
app.include_router(publishing_router, prefix="/api")
app.include_router(ebooks_router, prefix="/api")
app.include_router(audiobooks_router, prefix="/api")
app.include_router(videos_router, prefix="/api")
app.include_router(saga_loader_router, prefix="/api")
app.include_router(saga_runtime_router, prefix="/api")
app.include_router(system_smoke_router, prefix="/api")
app.include_router(story_layout_router, prefix="/api")
app.include_router(illustration_pipeline_router, prefix="/api")
app.include_router(illustration_assets_router, prefix="/api")
app.include_router(illustration_generation_router, prefix="/api")
app.include_router(illustration_provider_router, prefix="/api")
app.include_router(age_badges_router, prefix="/api")
app.include_router(covers_router, prefix="/api")
app.include_router(ip_creator_router, prefix="/api")
app.include_router(ip_palette_router, prefix="/api")
app.include_router(ip_branding_router, prefix="/api")
app.include_router(ip_characters_router, prefix="/api")
app.include_router(ip_canons_router, prefix="/api")
app.include_router(ip_metadata_router, prefix="/api")
app.include_router(illustrations_router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {
        "ok": True,
        "app_name": APP_CONFIG.app_name,
        "version": APP_CONFIG.app_version,
        "docs": "/docs",
        "health": "/api/health",
        "diagnostics": "/api/diagnostics",
}
