from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.storage import read_json
from studio_core.services.system_smoke_service import run_system_smoke

router = APIRouter(prefix="/system-smoke", tags=["system-smoke"])

SMOKE_RESULTS_FILE = "data/smoke_results.json"


@router.get("")
def list_smoke_results() -> dict:
    results = read_json(SMOKE_RESULTS_FILE, [])
    if not isinstance(results, list):
        results = []
    return {
        "ok": True,
        "results": results,
    }


@router.post("/{project_id}")
def run_smoke(project_id: str) -> dict:
    try:
        result = run_system_smoke(project_id)
        return {
            "ok": True,
            "result": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
