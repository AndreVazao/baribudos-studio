from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.updater_service import check_for_updates, download_update, get_local_version_info
from studio_core.services.auth_principal import require_roles

router = APIRouter(prefix="/updater", dependencies=[Depends(require_roles("owner", "admin"))], tags=["updater"])


@router.get("/local-version")
def local_version() -> dict:
    return {
        "ok": True,
        "version": get_local_version_info(),
    }


@router.post("/check")
def check_updates(payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return check_for_updates(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/download")
def download_updates(payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return download_update(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
