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


def _safe_list(value):
    return value if isinstance(value, list) else []


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


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

        visual_identity = _safe_dict(char.get("visual_identity"))
        wardrobe_identity = _safe_dict(char.get("wardrobe_identity"))
        consistency_rules = _safe_dict(char.get("consistency_rules"))
        reference_assets = _safe_dict(char.get("reference_assets"))
        prompt_guardrails = _safe_dict(char.get("prompt_guardrails"))

        normalized.append({
            "id": str(char.get("id", "")).strip(),
            "name": str(char.get("name", "")).strip(),
            "role": str(char.get("role", "")).strip(),
            "age": char.get("age"),
            "archetype": str(char.get("archetype", "")).strip(),
            "traits": _safe_list(char.get("traits")),
            "accent_color": str(char.get("accent_color", "")).strip(),
            "signature_item": str(char.get("signature_item", "")).strip(),
            "visual_identity": {
                "species": str(visual_identity.get("species", "")).strip(),
                "body_shape": str(visual_identity.get("body_shape", "")).strip(),
                "fur_primary": str(visual_identity.get("fur_primary", "")).strip(),
                "fur_secondary": str(visual_identity.get("fur_secondary", "")).strip(),
                "hair_style": str(visual_identity.get("hair_style", "")).strip(),
                "eye_shape": str(visual_identity.get("eye_shape", "")).strip(),
                "eye_color": str(visual_identity.get("eye_color", "")).strip(),
                "nose_shape": str(visual_identity.get("nose_shape", "")).strip(),
                "beard_style": str(visual_identity.get("beard_style", "")).strip(),
                "distinctive_marks": _safe_list(visual_identity.get("distinctive_marks")),
                "silhouette_keywords": _safe_list(visual_identity.get("silhouette_keywords")),
            },
            "wardrobe_identity": {
                "core_outfit": str(wardrobe_identity.get("core_outfit", "")).strip(),
                "accessories": _safe_list(wardrobe_identity.get("accessories")),
                "forbidden_changes": _safe_list(wardrobe_identity.get("forbidden_changes")),
            },
            "consistency_rules": {
                "must_keep": _safe_list(consistency_rules.get("must_keep")),
                "can_vary": _safe_list(consistency_rules.get("can_vary")),
                "never_change": _safe_list(consistency_rules.get("never_change")),
            },
            "reference_assets": {
                "front": str(reference_assets.get("front", "")).strip(),
                "side": str(reference_assets.get("side", "")).strip(),
                "expression_sheet": str(reference_assets.get("expression_sheet", "")).strip(),
                "turnaround": str(reference_assets.get("turnaround", "")).strip(),
            },
            "prompt_guardrails": {
                "positive": _safe_list(prompt_guardrails.get("positive")),
                "negative": _safe_list(prompt_guardrails.get("negative")),
            },
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
