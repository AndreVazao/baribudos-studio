from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from studio_core.services.auth_principal import require_roles
from studio_core.services.local_audio_installer_service import get_local_audio_status, set_local_audio_default_provider, setup_local_audio_installer
router = APIRouter(prefix="/local-audio", dependencies=[Depends(require_roles("owner", "admin"))], tags=["local-audio"])
@router.get("/status")
def status() -> dict: return {"ok": True, "status": get_local_audio_status()}
@router.post("/setup")
def setup(payload: dict | None = None) -> dict:
    try: return setup_local_audio_installer(payload or {})
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
@router.post("/default-provider")
def default_provider(payload: dict | None = None) -> dict:
    try: return set_local_audio_default_provider(str((payload or {}).get("provider", "")).strip())
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
