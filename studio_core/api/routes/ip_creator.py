from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.ip_creator_service import (
    create_ip,
    ensure_ip_folder_structure,
    get_ip_by_slug,
    get_ip_schema_template,
    list_ip_assets_schema,
    update_ip,
)
from studio_core.services.ip_route_auth import (
    assert_ip_edit_access,
    require_ip_edit_access,
    require_ip_read_access,
    list_ips_visible_to_principal,
)

router = APIRouter(prefix="/ip-creator", tags=["ip-creator"])
_IP_ROLES = ("owner", "admin", "editor", "creator")
_EDITABLE_FIELDS = {
    "name", "status", "default_language", "output_languages",
    "metadata", "brand_assets", "palette", "main_characters",
}


@router.get("/schema")
def ip_schema(principal: AuthenticatedPrincipal = Depends(require_roles(*_IP_ROLES))) -> dict:
    return {"ok": True, "schema": get_ip_schema_template()}


@router.get("/assets-schema")
def assets_schema(principal: AuthenticatedPrincipal = Depends(require_roles(*_IP_ROLES))) -> dict:
    return {"ok": True, "assets_schema": list_ip_assets_schema()}


@router.get("")
def ips(principal: AuthenticatedPrincipal = Depends(require_roles(*_IP_ROLES))) -> dict:
    return {"ok": True, "ips": list_ips_visible_to_principal(principal)}


@router.get("/all")
def all_ips(principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin"))) -> dict:
    from studio_core.services.ip_creator_service import list_ips
    return {"ok": True, "ips": list_ips()}


@router.get("/{slug}")
def ip_by_slug(
    slug: str,
    principal: AuthenticatedPrincipal = Depends(require_ip_read_access),
) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")
    return {"ok": True, "ip": item}


@router.post("")
def new_ip(
    payload: dict,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    safe_payload = {key: value for key, value in (payload or {}).items() if key in _EDITABLE_FIELDS}
    safe_payload["owner_id"] = principal.user_id
    safe_payload["owner_name"] = principal.name
    safe_payload["visible_to_owner_only"] = True
    safe_payload["exclusive"] = False
    try:
        item = create_ip(safe_payload)
        return {"ok": True, "ip": item}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{slug}")
def patch_ip(
    slug: str,
    payload: dict,
    principal: AuthenticatedPrincipal = Depends(require_ip_edit_access),
) -> dict:
    safe_patch = {key: value for key, value in (payload or {}).items() if key in _EDITABLE_FIELDS}
    try:
        item = update_ip(slug, safe_patch)
        return {"ok": True, "ip": item}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{slug}/ensure-folders")
def ensure_folders(
    slug: str,
    principal: AuthenticatedPrincipal = Depends(require_ip_edit_access),
) -> dict:
    path = ensure_ip_folder_structure(slug)
    return {"ok": True, "path": path}


@router.get("/{slug}/permissions")
def ip_permissions(
    slug: str,
    principal: AuthenticatedPrincipal = Depends(require_ip_read_access),
) -> dict:
    item = get_ip_by_slug(slug) or {}
    try:
        assert_ip_edit_access(slug, principal)
        can_edit = True
    except HTTPException:
        can_edit = False
    can_publish = principal.role.lower() in {"owner", "admin"} or (
        can_edit and principal.role.lower() in set(item.get("publishable_by_roles") or [])
    )
    return {"ok": True, "can_edit": can_edit, "can_publish": can_publish}
