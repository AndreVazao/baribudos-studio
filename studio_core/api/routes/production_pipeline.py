from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.production_pipeline_service import list_production_runs, run_production_pipeline

router = APIRouter(prefix="/production-pipeline", tags=["production-pipeline"])


@router.get("")
def get_production_runs() -> dict:
    return {
        "ok": True,
        "runs": list_production_runs(),
    }


@router.post("/run/{project_id}")
def run_pipeline(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return run_production_pipeline(project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
