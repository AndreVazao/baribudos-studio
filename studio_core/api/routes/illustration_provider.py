from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.illustration_generation_runtime_service import run_local_illustration_generation
from studio_core.services.project_route_auth import require_project_path_access

router = APIRouter(prefix="/illustration-provider", tags=["illustration-provider"])


@router.post("/run/{project_id}")
def run_provider(project_id: str, payload: dict | None = None, _principal=Depends(require_project_path_access)) -> dict:
    try:
        return run_local_illustration_generation(project_id, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Não foi possível executar o fornecedor de ilustração.") from exc
