from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.ip_creator_service import can_edit_ip, get_ip_by_slug, update_ip

router = APIRouter(prefix="/ip-metadata", tags=["ip-metadata"])


def _user_from_payload_or_query(payload: dict | None = None, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    payload = payload or {}
    return {
        "id": str(payload.get("user_id", user_id)).strip(),
        "name": str(payload.get("user_name", user_name)).strip(),
        "role": str(payload.get("user_role", user_role)).strip()
    }


@router.get("/{slug}")
def get_metadata(slug: str, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(user_id=user_id, user_name=user_name, user_role=user_role)
    if not can_edit_ip(user, slug) and str(item.get("owner_id", "")).strip() != str(user.get("id", "")).strip():
        raise HTTPException(status_code=403, detail="Sem permissão para ver metadados desta IP.")

    return {
        "ok": True,
        "slug": slug,
        "metadata": item.get("metadata", {}),
        "default_language": item.get("default_language", "pt-PT"),
        "output_languages": item.get("output_languages", ["pt-PT"])
    }


@router.patch("/{slug}")
def patch_metadata(slug: str, payload: dict) -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(payload)
    if not can_edit_ip(user, slug):
        raise HTTPException(status_code=403, detail="Sem permissão para editar metadados desta IP.")

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
