from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.ip_creator_service import can_edit_ip, get_ip_by_slug, update_ip

router = APIRouter(prefix="/ip-characters", tags=["ip-characters"])


def _user_from_payload_or_query(payload: dict | None = None, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    payload = payload or {}
    return {
        "id": str(payload.get("user_id", user_id)).strip(),
        "name": str(payload.get("user_name", user_name)).strip(),
        "role": str(payload.get("user_role", user_role)).strip()
    }


@router.get("/{slug}")
def get_characters(slug: str, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(user_id=user_id, user_name=user_name, user_role=user_role)
    if not can_edit_ip(user, slug) and str(item.get("owner_id", "")).strip() != str(user.get("id", "")).strip():
        raise HTTPException(status_code=403, detail="Sem permissão para ver personagens desta IP.")

    return {
        "ok": True,
        "slug": slug,
        "main_characters": item.get("main_characters", [])
    }


@router.patch("/{slug}")
def patch_characters(slug: str, payload: dict) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(payload)
    if not can_edit_ip(user, slug):
        raise HTTPException(status_code=403, detail="Sem permissão para editar personagens desta IP.")

    main_characters = payload.get("main_characters")
    if not isinstance(main_characters, list):
        raise HTTPException(status_code=400, detail="main_characters inválido.")

    normalized = []
    for char in main_characters:
        if not isinstance(char, dict):
            continue

        normalized.append({
            "id": str(char.get("id", "")).strip(),
            "name": str(char.get("name", "")).strip(),
            "role": str(char.get("role", "")).strip(),
            "age": char.get("age"),
            "archetype": str(char.get("archetype", "")).strip(),
            "traits": char.get("traits") if isinstance(char.get("traits"), list) else [],
            "accent_color": str(char.get("accent_color", "")).strip(),
            "signature_item": str(char.get("signature_item", "")).strip(),
        })

    try:
        updated = update_ip(slug, {"main_characters": normalized})
        return {
            "ok": True,
            "slug": slug,
            "main_characters": updated.get("main_characters", []),
            "ip": updated
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
