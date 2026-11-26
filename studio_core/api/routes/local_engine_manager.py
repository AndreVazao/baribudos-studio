from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from studio_core.services.auth_principal import require_roles
from studio_core.services.local_engine_manager_service import ensure_provider_running, get_engine_manager_status, start_provider, stop_provider
router = APIRouter(prefix="/local-engine-manager", dependencies=[Depends(require_roles("owner", "admin"))], tags=["local-engine-manager"])
@router.get("/status")
def status() -> dict:
    try: return {"ok": True, "status": get_engine_manager_status()}
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
@router.post("/start")
def start(payload: dict | None = None) -> dict:
    try: return start_provider(str((payload or {}).get("provider", "")).strip())
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
@router.post("/ensure")
def ensure(payload: dict | None = None) -> dict:
    try: return ensure_provider_running(str((payload or {}).get("provider", "")).strip())
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
@router.post("/stop")
def stop(payload: dict | None = None) -> dict:
    try: return stop_provider(str((payload or {}).get("provider", "")).strip())
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
