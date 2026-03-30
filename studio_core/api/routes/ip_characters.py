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


def _blank(value) -> bool:
    return str(value or "").strip() == ""


def _character_consistency_report(char: dict) -> dict:
    visual_identity = _safe_dict(char.get("visual_identity"))
    wardrobe_identity = _safe_dict(char.get("wardrobe_identity"))
    consistency_rules = _safe_dict(char.get("consistency_rules"))
    prompt_guardrails = _safe_dict(char.get("prompt_guardrails"))

    missing = []

    if _blank(char.get("name")):
        missing.append("name")
    if _blank(char.get("role")):
        missing.append("role")
    if _blank(char.get("archetype")):
        missing.append("archetype")
    if len(_safe_list(char.get("traits"))) == 0:
        missing.append("traits")
    if _blank(char.get("accent_color")):
        missing.append("accent_color")
    if _blank(char.get("signature_item")):
        missing.append("signature_item")

    for key in ["species", "body_shape", "fur_primary", "hair_style", "eye_shape", "eye_color", "beard_style"]:
        if _blank(visual_identity.get(key)):
            missing.append(f"visual_identity.{key}")

    if len(_safe_list(visual_identity.get("distinctive_marks"))) == 0:
        missing.append("visual_identity.distinctive_marks")
    if len(_safe_list(visual_identity.get("silhouette_keywords"))) == 0:
        missing.append("visual_identity.silhouette_keywords")

    if _blank(wardrobe_identity.get("core_outfit")):
        missing.append("wardrobe_identity.core_outfit")
    if len(_safe_list(wardrobe_identity.get("forbidden_changes"))) == 0:
        missing.append("wardrobe_identity.forbidden_changes")

    for key in ["must_keep", "never_change"]:
        if len(_safe_list(consistency_rules.get(key))) == 0:
            missing.append(f"consistency_rules.{key}")

    for key in ["positive", "negative"]:
        if len(_safe_list(prompt_guardrails.get(key))) == 0:
            missing.append(f"prompt_guardrails.{key}")

    return {
        "id": str(char.get("id", "")).strip(),
        "name": str(char.get("name", "")).strip(),
        "role": str(char.get("role", "")).strip(),
        "status": "complete" if len(missing) == 0 else "needs_attention",
        "missing": missing,
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


@router.get("/{slug}/consistency-summary")
def get_characters_consistency_summary(slug: str, user_id: str = "", user_name: str = "", user_role: str = "") -> dict:
    item = get_ip_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="IP não encontrada.")

    user = _user_from_payload_or_query(user_id=user_id, user_name=user_name, user_role=user_role)
    if not can_edit_ip(user, slug) and str(item.get("owner_id", "")).strip() != str(user.get("id", "")).strip():
        raise HTTPException(status_code=403, detail="Sem permissão para ver consistência desta IP.")

    reports = [_character_consistency_report(char) for char in _safe_list(item.get("main_characters")) if isinstance(char, dict)]

    return {
        "ok": True,
        "slug": slug,
        "count": len(reports),
        "complete": len([r for r in reports if r.get("status") == "complete"]),
        "needs_attention": len([r for r in reports if r.get("status") == "needs_attention"]),
        "reports": reports,
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
