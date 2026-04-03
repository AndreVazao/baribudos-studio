from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.sponsorship_scope_service import (
    create_sponsorship_scope,
    list_sponsorship_scopes,
    patch_sponsorship_scope,
    resolve_sponsorship_for_project,
)

router = APIRouter(prefix="/sponsorship-scopes", tags=["sponsorship-scopes"])


@router.get("")
def get_scopes() -> dict:
    return {"ok": True, "items": list_sponsorship_scopes()}


@router.post("")
def post_scope(payload: dict | None = None) -> dict:
    try:
        return {"ok": True, "item": create_sponsorship_scope(payload or {})}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{scope_id}")
def patch_scope(scope_id: str, payload: dict | None = None) -> dict:
    try:
        return {"ok": True, "item": patch_sponsorship_scope(scope_id, payload or {})}
    except ValueError as exc:
        status = 404 if str(exc) == "sponsorship_scope_not_found" else 400
        raise HTTPException(status_code=status, detail=str(exc)) from exc


@router.get("/resolve/{project_id}")
def resolve_scope(project_id: str) -> dict:
    try:
        return resolve_sponsorship_for_project(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
