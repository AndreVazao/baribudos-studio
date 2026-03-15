from __future__ import annotations

from fastapi import APIRouter

from studio_core.services.project_factory_runtime_service import (
    load_project_factory_context
)

router = APIRouter()


@router.post("/factory/context")
def factory_context(payload: dict):

    ip_slug = payload.get("ip_slug")

    if not ip_slug:
        return {
            "ok": False,
            "error": "ip_slug obrigatório"
        }

    context = load_project_factory_context(
        ip_slug=ip_slug,
        project_payload=payload
    )

    return {
        "ok": True,
        "context": context
    }
