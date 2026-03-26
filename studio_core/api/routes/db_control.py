from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.db_control_service import (
    get_db_control_readiness,
    get_db_control_status,
)

router = APIRouter(prefix="/db-control", tags=["db-control"])


@router.get("/status")
def db_control_status() -> dict:
    try:
        return {
            "ok": True,
            "database": get_db_control_status(),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/readiness")
def db_control_readiness() -> dict:
    try:
        return {
            "ok": True,
            "database": get_db_control_readiness(),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
