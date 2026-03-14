from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.ip_creator_service import (
    can_edit_ip,
    can_publish_ip,
    create_ip,
    ensure_ip_folder_structure,
    get_ip_by_slug,
    get_ip_schema_template,
    list_ip_assets_schema,
    list_ips,
    list_ips_for_user,
    update_ip,
)

router = APIRouter(prefix="/ip-creator", tags=["ip-creator"])


def _user_from_payload_or_query(payload: dict | None = None, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    payload = payload or {}
    return {
        "id": str(payload.get("user_id", user_id)).strip(),
        "name": str(payload.get("user_name", user_name)).strip(),
        "role": str(payload.get("user_role", user_role)).strip()
    }


@router.get("/schema")
def ip_schema() -> dict:
    return {"ok": True, "schema": get_ip_schema_template()}


@router.get("/assets-schema")
def assets_schema() -> dict:
    return {"ok": True, "assets_schema": list_ip_assets_schema()}


@router.get("")
def ips(user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    user = _user_from_payload_or_query(user_id=user_id, user_name=user_name, user_role=user_role)
    items = list_ips_for_user(user if any(user.values()) else None)
    return {"ok": True, "ips": items}


@router.get("/all")
def all_ips() -> dict:
    return {"ok": True, "ips": list_ips()}


@router.get("/{slug}")
def ip_by_slug(slug: str, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(user_id=user_id, user_name=user_name, user_role=user_role)
    visible = list_ips_for_user(user if any(user.values()) else None)
    if not any(str(ip.get("slug", "")) == str(item.get("slug", "")) for ip in visible):
        raise HTTPException(status_code=403, detail="Sem acesso a esta IP.")

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
    user = _user_from_payload_or_query(payload)
    if not can_edit_ip(user, slug):
        raise HTTPException(status_code=403, detail="Sem permissão para editar esta IP.")

    try:
        item = update_ip(slug, payload or {})
        return {"ok": True, "ip": item}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{slug}/ensure-folders")
def ensure_folders(slug: str, payload: dict | None = None) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(payload)
    if not can_edit_ip(user, slug):
        raise HTTPException(status_code=403, detail="Sem permissão para preparar esta IP.")

    path = ensure_ip_folder_structure(slug)
    return {"ok": True, "path": path}


@router.get("/{slug}/permissions")
def ip_permissions(slug: str, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    user = _user_from_payload_or_query(user_id=user_id, user_name=user_name, user_role=user_role)
    return {
        "ok": True,
        "can_edit": can_edit_ip(user, slug),
        "can_publish": can_publish_ip(user, slug)
           }
