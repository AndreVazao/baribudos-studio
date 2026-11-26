from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.ip_creator_service import get_ip_by_slug
from studio_core.services.ip_route_auth import assert_ip_read_access
from studio_core.services.saga_runtime_service import load_saga_runtime
router = APIRouter(prefix="/saga-runtime", tags=["saga-runtime"])
@router.get("/{slug}")
def get_saga_runtime(slug: str, principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator"))) -> dict:
    assert_ip_read_access(slug, principal)
    canonical = str((get_ip_by_slug(slug) or {}).get("slug", slug))
    try: return {"ok": True, "runtime": load_saga_runtime(canonical)}
    except FileNotFoundError as exc: raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
