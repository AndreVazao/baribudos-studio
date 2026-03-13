from __future__ import annotations

from fastapi import APIRouter

from studio_core.services.publishing_service import create_publication_record, list_publications

router = APIRouter(prefix="/publishing", tags=["publishing"])


@router.get("")
def publications() -> dict:
    return {"ok": True, "publications": list_publications()}


@router.post("/publish")
def publish(payload: dict) -> dict:
    result = create_publication_record(payload or {})
    return {"ok": True, "publication": result}
