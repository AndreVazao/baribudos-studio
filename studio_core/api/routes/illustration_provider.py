from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.illustration_generation_runtime_service import run_local_illustration_generation

router = APIRouter(prefix="/illustration-provider", tags=["illustration-provider"])


@router.post("/run/{project_id}")
def run_provider(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        return run_local_illustration_generation(project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
