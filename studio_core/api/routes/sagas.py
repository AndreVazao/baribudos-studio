from __future__ import annotations
import re
from fastapi import APIRouter, Depends, HTTPException
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.saga_service import list_sagas, create_saga, update_saga
router = APIRouter(prefix="/sagas", tags=["sagas"])
_READ_ROLES = ("owner", "admin", "editor", "creator")
_MUTABLE_FIELDS = {"slug", "name", "colors", "characters_locked", "sponsors", "typography"}
@router.get("")
def get_sagas(principal: AuthenticatedPrincipal = Depends(require_roles(*_READ_ROLES))):
    return list_sagas()
@router.post("")
def new_saga(payload: dict, principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin"))):
    safe_payload = {key: value for key, value in (payload or {}).items() if key in _MUTABLE_FIELDS}
    slug = str(safe_payload.get("slug", "")).strip()
    if not slug or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", slug):
        raise HTTPException(status_code=400, detail="slug inválido.")
    safe_payload["created_by"] = principal.user_id
    return create_saga(safe_payload)
@router.patch("/{slug}")
def patch_saga(slug: str, payload: dict, principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin"))):
    try:
        safe_payload = {key: value for key, value in (payload or {}).items() if key in _MUTABLE_FIELDS and key != "slug"}
        return {"ok": True, "saga": update_saga(slug, safe_payload)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
