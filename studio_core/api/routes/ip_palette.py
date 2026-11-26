from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.ip_creator_service import get_ip_by_slug, update_ip
from studio_core.services.auth_principal import AuthenticatedPrincipal
from studio_core.services.ip_route_auth import require_ip_edit_access, require_ip_read_access

router = APIRouter(prefix="/ip-palette", tags=["ip-palette"])


@router.get("/{slug}")
def get_palette(slug: str, principal: AuthenticatedPrincipal = Depends(require_ip_read_access)) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    return {
        "ok": True,
        "slug": slug,
        "palette": item.get("palette", {})
    }


@router.patch("/{slug}")
def patch_palette(slug: str, payload: dict, principal: AuthenticatedPrincipal = Depends(require_ip_edit_access)) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    palette = payload.get("palette") or {}
    if not isinstance(palette, dict):
        raise HTTPException(status_code=400, detail="Palette inválida.")

    try:
        updated = update_ip(slug, {"palette": palette})
        return {
            "ok": True,
            "slug": slug,
            "palette": updated.get("palette", {}),
            "ip": updated
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
