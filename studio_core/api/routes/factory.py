from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.factory_service import get_factory_capabilities, run_factory
from studio_core.services.project_factory_runtime_service import load_project_factory_context

router = APIRouter(prefix="/factory", tags=["factory"])


@router.get("/capabilities")
def capabilities() -> dict:
    return {
        "ok": True,
        "capabilities": get_factory_capabilities(),
    }


@router.post("/context")
def factory_context(payload: dict) -> dict:
    ip_slug = str(payload.get("ip_slug", "")).strip()
    if not ip_slug:
        raise HTTPException(status_code=400, detail="ip_slug obrigatório")

    context = load_project_factory_context(
        ip_slug=ip_slug,
        project_payload=payload,
    )

    return {
        "ok": True,
        "context": context,
    }


@router.post("/run/{project_id}")
def factory_run(project_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    try:
        result = run_factory(project_id, payload)
        return {
            "ok": True,
            "result": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
