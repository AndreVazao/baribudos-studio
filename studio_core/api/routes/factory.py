from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.factory_service import get_factory_capabilities, run_factory

router = APIRouter(prefix="/factory", tags=["factory"])


@router.get("/capabilities")
def factory_capabilities() -> dict:
    return {"ok": True, "capabilities": get_factory_capabilities()}


@router.post("/run/{project_id}")
def factory_run(project_id: str, payload: dict) -> dict:
    try:
        result = run_factory(project_id, payload or {})
        return {"ok": True, "result": result}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
