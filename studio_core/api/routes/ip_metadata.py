from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from studio_core.services.ip_creator_service import get_ip_by_slug, update_ip
from studio_core.services.auth_principal import AuthenticatedPrincipal
from studio_core.services.ip_route_auth import require_ip_edit_access, require_ip_read_access

router = APIRouter(prefix="/ip-metadata", tags=["ip-metadata"])


@router.get("/{slug}")
def get_metadata(slug: str, principal: AuthenticatedPrincipal = Depends(require_ip_read_access)) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    return {
        "ok": True,
        "slug": slug,
        "metadata": item.get("metadata", {}),
        "default_language": item.get("default_language", "pt-PT"),
        "output_languages": item.get("output_languages", ["pt-PT"])
    }


@router.patch("/{slug}")
def patch_metadata(slug: str, payload: dict, principal: AuthenticatedPrincipal = Depends(require_ip_edit_access)) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    metadata = payload.get("metadata") or {}
    default_language = str(payload.get("default_language", item.get("default_language", "pt-PT"))).strip()
    output_languages = payload.get("output_languages", item.get("output_languages", ["pt-PT"]))

    if not isinstance(metadata, dict):
        raise HTTPException(status_code=400, detail="metadata inválido.")

    if not isinstance(output_languages, list) or not output_languages:
        raise HTTPException(status_code=400, detail="output_languages inválido.")

    try:
        updated = update_ip(
            slug,
            {
                "metadata": metadata,
                "default_language": default_language,
                "output_languages": output_languages
            }
        )
        return {
            "ok": True,
            "slug": slug,
            "metadata": updated.get("metadata", {}),
            "default_language": updated.get("default_language", "pt-PT"),
            "output_languages": updated.get("output_languages", ["pt-PT"]),
            "ip": updated
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
