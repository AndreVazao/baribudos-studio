from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from studio_core.api.routes.age_badges import router as age_badges_router
from studio_core.api.routes.assets import router as assets_router
from studio_core.api.routes.audio_cast import router as audio_cast_router
from studio_core.api.routes.audio_cast_preview import router as audio_cast_preview_router
from studio_core.api.routes.audiobooks import router as audiobooks_router
from studio_core.api.routes.branding_pack import router as branding_pack_router
from studio_core.api.routes.commerce_groups import router as commerce_groups_router
from studio_core.api.routes.covers import router as covers_router
from studio_core.api.routes.db_control import router as db_control_router
from studio_core.api.routes.deploy_control import router as deploy_control_router
from studio_core.api.routes.diagnostics import router as diagnostics_router
from studio_core.api.routes.editorial_engine import router as editorial_engine_router
from studio_core.api.routes.editorial_media_pipeline import router as editorial_media_pipeline_router
from studio_core.api.routes.editorial_production import router as editorial_production_router
from studio_core.api.routes.ebooks import router as ebooks_router
from studio_core.api.routes.factory import router as factory_router
from studio_core.api.routes.final_media_render import router as final_media_render_router
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
from studio_core.api.routes.local_ai_installer import router as local_ai_installer_router
from studio_core.api.routes.local_ai_runtime import router as local_ai_runtime_router
from studio_core.api.routes.local_audio_engine_manager import router as local_audio_engine_manager_router
from studio_core.api.routes.local_audio_installer import router as local_audio_installer_router
from studio_core.api.routes.local_engine_manager import router as local_engine_manager_router
from studio_core.api.routes.marketplace_visuals import router as marketplace_visuals_router
from studio_core.api.routes.pairing import router as pairing_router
from studio_core.api.routes.production_pipeline import router as production_pipeline_router
from studio_core.api.routes.project_commercial import router as project_commercial_router
from studio_core.api.routes.project_integrity import router as project_integrity_router
from studio_core.api.routes.projects import router as projects_router
from studio_core.api.routes.public_assets import router as public_assets_router
from studio_core.api.routes.publication_package import router as publication_package_router
from studio_core.api.routes.publish_readiness import router as publish_readiness_router
from studio_core.api.routes.publishing import router as publishing_router
from studio_core.api.routes.saga_loader import router as saga_loader_router
from studio_core.api.routes.saga_runtime import router as saga_runtime_router
from studio_core.api.routes.sagas import router as sagas_router
from studio_core.api.routes.secret_control import router as secret_control_router
from studio_core.api.routes.settings import router as settings_router
from studio_core.api.routes.sponsors import router as sponsors_router
from studio_core.api.routes.storefront import router as storefront_router
from studio_core.api.routes.story_layout import router as story_layout_router
from studio_core.api.routes.system_smoke import router as system_smoke_router
from studio_core.api.routes.system_smoke_v1 import router as system_smoke_v1_router
from studio_core.api.routes.updater import router as updater_router
from studio_core.api.routes.users import ensure_default_owner, router as users_router
from studio_core.api.routes.v1_readiness import router as v1_readiness_router
from studio_core.api.routes.videos import router as videos_router
from studio_core.api.routes.voice_library import router as voice_library_router
from studio_core.api.routes.voice_preview import router as voice_preview_router
from studio_core.api.routes.website_admin import router as website_admin_router
from studio_core.api.routes.website_contract import router as website_contract_router
from studio_core.api.routes.website_control import router as website_control_router
from studio_core.api.routes.website_publisher import router as website_publisher_router
from studio_core.core.config import APP_CONFIG, resolve_project_path, resolve_storage_path
from studio_core.services.ai_runtime_bootstrap import start_all
from studio_core.services.bootstrap_service import bootstrap_system


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_system()
    ensure_default_owner()
    start_all()
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
app.include_router(system_smoke_v1_router, prefix="/api")
app.include_router(story_layout_router, prefix="/api")
app.include_router(editorial_engine_router, prefix="/api")
app.include_router(editorial_production_router, prefix="/api")
app.include_router(editorial_media_pipeline_router, prefix="/api")
app.include_router(final_media_render_router, prefix="/api")
app.include_router(illustration_pipeline_router, prefix="/api")
app.include_router(illustration_assets_router, prefix="/api")
app.include_router(illustration_generation_router, prefix="/api")
app.include_router(illustration_provider_router, prefix="/api")
app.include_router(local_ai_installer_router, prefix="/api")
app.include_router(local_ai_runtime_router, prefix="/api")
app.include_router(local_engine_manager_router, prefix="/api")
app.include_router(local_audio_installer_router, prefix="/api")
app.include_router(local_audio_engine_manager_router, prefix="/api")
app.include_router(voice_library_router, prefix="/api")
app.include_router(voice_preview_router, prefix="/api")
app.include_router(audio_cast_router, prefix="/api")
app.include_router(audio_cast_preview_router, prefix="/api")
app.include_router(updater_router, prefix="/api")
app.include_router(v1_readiness_router, prefix="/api")
app.include_router(age_badges_router, prefix="/api")
app.include_router(covers_router, prefix="/api")
app.include_router(ip_creator_router, prefix="/api")
app.include_router(ip_palette_router, prefix="/api")
app.include_router(ip_branding_router, prefix="/api")
app.include_router(ip_characters_router, prefix="/api")
app.include_router(ip_canons_router, prefix="/api")
app.include_router(ip_metadata_router, prefix="/api")
app.include_router(illustrations_router, prefix="/api")
app.include_router(assets_router, prefix="/api")
app.include_router(website_contract_router, prefix="/api")
app.include_router(branding_pack_router, prefix="/api")
app.include_router(marketplace_visuals_router, prefix="/api")
app.include_router(pairing_router, prefix="/api")
app.include_router(website_publisher_router, prefix="/api")
app.include_router(website_control_router, prefix="/api")
app.include_router(website_admin_router, prefix="/api")
app.include_router(deploy_control_router, prefix="/api")
app.include_router(db_control_router, prefix="/api")
app.include_router(commerce_groups_router, prefix="/api")
app.include_router(secret_control_router, prefix="/api")
app.include_router(public_assets_router, prefix="/api")
app.include_router(storefront_router)


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
