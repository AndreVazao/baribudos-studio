from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.ip_creator_service import can_edit_ip, get_ip_by_slug, update_ip

router = APIRouter(prefix="/ip-palette", tags=["ip-palette"])


def _user_from_payload_or_query(payload: dict | None = None, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    payload = payload or {}
    return {
        "id": str(payload.get("user_id", user_id)).strip(),
        "name": str(payload.get("user_name", user_name)).strip(),
        "role": str(payload.get("user_role", user_role)).strip()
    }


@router.get("/{slug}")
def get_palette(slug: str, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(user_id=user_id, user_name=user_name, user_role=user_role)
    if not can_edit_ip(user, slug) and str(item.get("owner_id", "")).strip() != str(user.get("id", "")).strip():
        raise HTTPException(status_code=403, detail="Sem permissão para ver a paleta desta IP.")

    return {
        "ok": True,
        "slug": slug,
        "palette": item.get("palette", {})
    }


@router.patch("/{slug}")
def patch_palette(slug: str, payload: dict) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(payload)
    if not can_edit_ip(user, slug):
        raise HTTPException(status_code=403, detail="Sem permissão para editar a paleta desta IP.")

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
