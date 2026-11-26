from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from studio_core.services.auth_principal import require_roles
from studio_core.services.local_audio_engine_manager_service import ensure_audio_provider_running, get_local_audio_engine_status, start_audio_provider, stop_audio_provider
router = APIRouter(prefix="/local-audio-engine-manager", dependencies=[Depends(require_roles("owner", "admin"))], tags=["local-audio-engine-manager"])
@router.get("/status")
def status() -> dict:
    try: return {"ok": True, "status": get_local_audio_engine_status()}
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
@router.post("/start")
def start(payload: dict | None = None) -> dict:
    try: return start_audio_provider(str((payload or {}).get("provider", "")).strip())
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
@router.post("/ensure")
def ensure(payload: dict | None = None) -> dict:
    try: return ensure_audio_provider_running(str((payload or {}).get("provider", "")).strip())
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
@router.post("/stop")
def stop(payload: dict | None = None) -> dict:
    try: return stop_audio_provider(str((payload or {}).get("provider", "")).strip())
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
