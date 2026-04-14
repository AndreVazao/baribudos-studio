from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.distribution_hub_service import (
    get_distribution_hub_snapshot,
    patch_distribution_hub,
    refresh_distribution_hub,
)

router = APIRouter(prefix="/distribution-hub", tags=["distribution-hub"])


def _normalize_name(value: str) -> str:
    return str(value or "").strip().lower()


def _can_edit_or_publish(user_role: str, user_name: str) -> bool:
    role = str(user_role or "").strip().lower()
    name = _normalize_name(user_name)
    return role in {"owner", "creator", "admin"} or name in {"andré", "andre", "esposa", "wife", "mama"}


@router.get("/{project_id}")
def get_distribution_hub(project_id: str) -> dict:
    try:
        snapshot = get_distribution_hub_snapshot(project_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {
        "ok": True,
        "project_id": project_id,
        "distribution_hub": snapshot,
    }


@router.post("/{project_id}/refresh")
def refresh_distribution_hub_endpoint(project_id: str, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão comercial/editorial.")

    try:
        snapshot = refresh_distribution_hub(project_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {
        "ok": True,
        "project_id": project_id,
        "distribution_hub": snapshot,
    }


@router.patch("/{project_id}")
def patch_distribution_hub_endpoint(project_id: str, payload: dict, user_name: str = "", user_role: str = "") -> dict:
    if not _can_edit_or_publish(user_role, user_name):
        raise HTTPException(status_code=403, detail="Sem permissão comercial/editorial.")

    patch = payload.get("distribution_hub") if isinstance(payload.get("distribution_hub"), dict) else payload
    if not isinstance(patch, dict):
        raise HTTPException(status_code=400, detail="distribution_hub inválido.")

    try:
        snapshot = patch_distribution_hub(project_id, patch)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {
        "ok": True,
        "project_id": project_id,
        "distribution_hub": snapshot,
    }
