from __future__ import annotations

from fastapi import APIRouter

from studio_core.core.config import APP_CONFIG

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "app_name": APP_CONFIG.app_name,
        "version": APP_CONFIG.app_version,
        "host": APP_CONFIG.host,
        "port": APP_CONFIG.port,
        "environment": APP_CONFIG.environment,
        "storage_root": str(APP_CONFIG.storage_root),
    }
