from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.system_smoke_v1_service import run_v1_smoke

router = APIRouter(prefix="/system-smoke-v1", tags=["system-smoke-v1"])


@router.get("")
def system_smoke_v1() -> dict:
    try:
        return run_v1_smoke()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
