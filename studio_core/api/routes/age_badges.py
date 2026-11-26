from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.ip_route_auth import assert_ip_edit_access
from studio_core.services.ip_creator_service import get_ip_by_slug
from studio_core.services.age_badge_service import generate_age_badge

router = APIRouter(prefix="/age-badges", tags=["age-badges"])


@router.post("/generate")
def create_age_badge(
    payload: dict,
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    saga_id = str(payload.get("saga_id", "baribudos")).strip()
    assert_ip_edit_access(saga_id, principal)
    ip = get_ip_by_slug(saga_id) or {}
    saga_id = str(ip.get("slug", saga_id))
    try:
        result = generate_age_badge(
            saga_id=saga_id,
            age_range=str(payload.get("age_range", "4-10")).strip(),
            language=str(payload.get("language", "pt-PT")).strip(),
            output_name=payload.get("output_name"),
        )
        return {"ok": True, "result": result}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
