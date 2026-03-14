from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.ip_creator_service import (
    can_edit_ip,
    create_ip,
    ensure_ip_folder_structure,
    get_ip_by_slug,
    get_ip_schema_template,
    list_ip_assets_schema,
    list_ips,
    update_ip,
)

router = APIRouter(prefix="/ip-creator", tags=["ip-creator"])


@router.get("/schema")
def ip_schema() -> dict:
    return {"ok": True, "schema": get_ip_schema_template()}


@router.get("/assets-schema")
def assets_schema() -> dict:
    return {"ok": True, "assets_schema": list_ip_assets_schema()}


@router.get("")
def ips() -> dict:
    return {"ok": True, "ips": list_ips()}


@router.get("/{slug}")
def ip_by_slug(slug: str) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")
    return {"ok": True, "ip": item}


@router.post("")
def new_ip(payload: dict) -> dict:
    try:
        item = create_ip(payload or {})
        return {"ok": True, "ip": item}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{slug}")
def patch_ip(slug: str, payload: dict) -> dict:
    try:
        item = update_ip(slug, payload or {})
        return {"ok": True, "ip": item}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{slug}/ensure-folders")
def ensure_folders(slug: str) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")
    path = ensure_ip_folder_structure(slug)
    return {"ok": True, "path": path}


@router.get("/{slug}/can-edit/{user_role}")
def ip_can_edit(slug: str, user_role: str) -> dict:
    return {"ok": True, "can_edit": can_edit_ip(user_role, slug)}
