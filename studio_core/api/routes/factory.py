from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.project_route_auth import assert_project_access
from studio_core.services.factory_service import get_factory_capabilities, run_factory

router = APIRouter(prefix="/factory", tags=["factory"])


@router.get("/capabilities")
def capabilities(principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin"))) -> dict:
    return {"ok": True, "capabilities": get_factory_capabilities()}


@router.post("/run/{project_id}")
def run_factory_endpoint(
    project_id: str,
    payload: dict | None = None,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    assert_project_access(project_id, principal)
    try:
        return {"ok": True, "result": run_factory(project_id, payload or {})}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
