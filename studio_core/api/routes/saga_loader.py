from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.saga_loader_service import (
    can_user_edit_saga,
    list_sagas_from_studio,
    load_saga,
    validate_story_structure,
    validate_visual_meta,
)

router = APIRouter(prefix="/saga-loader", tags=["saga-loader"])


@router.get("")
def list_sagas() -> dict:
    return {"ok": True, "sagas": list_sagas_from_studio()}


@router.get("/{saga_id}")
def get_saga(saga_id: str) -> dict:
    try:
        saga = load_saga(saga_id)
        return {"ok": True, "saga": saga}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{saga_id}/validate-story")
def validate_story(saga_id: str, payload: dict) -> dict:
    structure = payload.get("structure", []) or []
    result = validate_story_structure(saga_id, structure)
    return {"ok": True, "result": result}


@router.post("/{saga_id}/validate-visual")
def validate_visual(saga_id: str, payload: dict) -> dict:
    result = validate_visual_meta(saga_id, payload or {})
    return {"ok": True, "result": result}


@router.get("/{saga_id}/can-edit/{user_role}")
def can_edit_saga(saga_id: str, user_role: str) -> dict:
    return {
        "ok": True,
        "can_edit": can_user_edit_saga(user_role, saga_id)
  }
