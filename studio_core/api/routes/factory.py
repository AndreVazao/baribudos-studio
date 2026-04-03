from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.factory_service import (
    get_factory_capabilities,
    run_factory_for_project,
)

router = APIRouter(prefix="/factory", tags=["factory"])


@router.get("/capabilities")
def capabilities() -> dict:
    return {
        "ok": True,
        "capabilities": get_factory_capabilities(),
    }


@router.post("/run/{project_id}")
def run_factory(project_id: str, payload: dict | None = None) -> dict:
    try:
        return {
            "ok": True,
            "result": run_factory_for_project(project_id, payload or {}),
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
