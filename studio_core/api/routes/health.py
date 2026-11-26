from __future__ import annotations
from fastapi import APIRouter
from studio_core.core.config import APP_CONFIG
router = APIRouter()
@router.get("/health")
def health() -> dict:
    # Public liveness only: do not disclose host, port, environment or filesystem paths.
    return {"ok": True, "app_name": APP_CONFIG.app_name, "version": APP_CONFIG.app_version}
