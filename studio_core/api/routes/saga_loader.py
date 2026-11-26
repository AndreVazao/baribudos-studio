from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.ip_creator_service import get_ip_by_slug
from studio_core.services.ip_route_auth import assert_ip_edit_access, assert_ip_read_access
from studio_core.services.saga_loader_service import list_sagas_from_studio, load_saga, validate_story_structure, validate_visual_meta
router = APIRouter(prefix="/saga-loader", tags=["saga-loader"])
_READ_ROLES = ("owner", "admin", "editor", "creator")
@router.get("")
def list_sagas(principal: AuthenticatedPrincipal = Depends(require_roles(*_READ_ROLES))) -> dict:
    return {"ok": True, "sagas": list_sagas_from_studio()}
@router.get("/{saga_id}")
def get_saga(saga_id: str, principal: AuthenticatedPrincipal = Depends(require_roles(*_READ_ROLES))) -> dict:
    assert_ip_read_access(saga_id, principal)
    canonical = str((get_ip_by_slug(saga_id) or {}).get("slug", saga_id))
    try: return {"ok": True, "saga": load_saga(canonical)}
    except FileNotFoundError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
@router.post("/{saga_id}/validate-story")
def validate_story(saga_id: str, payload: dict, principal: AuthenticatedPrincipal = Depends(require_roles(*_READ_ROLES))) -> dict:
    assert_ip_read_access(saga_id, principal)
    canonical = str((get_ip_by_slug(saga_id) or {}).get("slug", saga_id))
    return {"ok": True, "result": validate_story_structure(canonical, payload.get("structure", []) or [])}
@router.post("/{saga_id}/validate-visual")
def validate_visual(saga_id: str, payload: dict, principal: AuthenticatedPrincipal = Depends(require_roles(*_READ_ROLES))) -> dict:
    assert_ip_read_access(saga_id, principal)
    canonical = str((get_ip_by_slug(saga_id) or {}).get("slug", saga_id))
    return {"ok": True, "result": validate_visual_meta(canonical, payload or {})}
@router.get("/{saga_id}/can-edit/{user_role}")
def can_edit_saga(saga_id: str, user_role: str, principal: AuthenticatedPrincipal = Depends(require_roles(*_READ_ROLES))) -> dict:
    # Preserve legacy URL shape; never trust its role segment.
    assert_ip_read_access(saga_id, principal)
    try: assert_ip_edit_access(saga_id, principal); can_edit = True
    except HTTPException: can_edit = False
    return {"ok": True, "can_edit": can_edit, "role": principal.role}
