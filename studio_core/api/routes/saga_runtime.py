from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.saga_runtime_service import load_saga_runtime

router = APIRouter(prefix="/saga-runtime", tags=["saga-runtime"])


@router.get("/{slug}")
def get_saga_runtime(slug: str) -> dict:
    try:
        runtime = load_saga_runtime(slug)
        return {
            "ok": True,
            "runtime": runtime,
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
