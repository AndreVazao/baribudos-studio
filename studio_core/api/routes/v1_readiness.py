from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.v1_readiness_service import get_v1_readiness

router = APIRouter(prefix="/v1-readiness", tags=["v1-readiness"])


@router.get("/{project_id}")
def readiness(project_id: str) -> dict:
    try:
        return get_v1_readiness(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
