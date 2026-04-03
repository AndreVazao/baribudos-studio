from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.models import now_iso
from studio_core.services.asset_registry_service import get_assets
from studio_core.services.branding_resolver_service import resolve_brand_assets
from studio_core.services.cdn_service import resolve_cdn_url
from studio_core.services.saga_runtime_service import load_saga_runtime
from studio_core.services.saga_service import list_sagas
from studio_core.services.voice_profile_service import get_voice_profile

REQUIRED_COMMERCIAL_FIELDS = ["internal_code", "price", "currency", "commercial_status"]
RECOMMENDED_COMMERCIAL_FIELDS = ["isbn", "asin", "subtitle", "blurb"]
REQUIRED_OUTPUT_GROUPS = ["covers", "epub"]
OPTIONAL_OUTPUT_GROUPS = ["audiobook", "video", "guide"]


def _normalize_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _has_value(value: Any) -> bool:
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return bool(_normalize_str(value))


def _resolve_typography(project: Dict[str, Any]) -> Dict[str, Any]:
    saga_slug = _normalize_str(project.get("saga_slug"))
    saga = next((item for item in list_sagas() if _normalize_str(item.get("slug")) == saga_slug), {})
    saga_typography = _safe_dict(_safe_dict(saga).get("typography", {}))
    project_typography = _safe_dict(_safe_dict(project.get("front_matter", {})).get("typography", {}))
    continuity = _safe_dict(project.get("continuity", {}))

    use_inherited = project_typography.get("use_inherited", True) is not False
    inherited_font = _normalize_str(saga_typography.get("font_family")) or "Georgia"
    project_font = _normalize_str(project_typography.get("font_family"))
    applied_font = inherited_font if use_inherited or not project_font else project_font
    preview_text = _normalize_str(project_typography.get("preview_text")) or _normalize_str(saga_typography.get("preview_text")) or _normalize_str(project.get("title")) or _normalize_str(continuity.get("hidden_universe_name"))

    return {
        "use_inherited": use_inherited,
        "saga_font_family": inherited_font,
        "project_font_family": project_font,
        "applied_font_family": applied_font,
        "preview_text": preview_text,
        "scope": "project" if not use_inherited and project_font else "saga",
    }


def _resolve_audio_credits(project: Dict[str, Any]) -> Dict[str, Any]:
    audio_cast = _safe_dict(project.get("audio_cast", {}))
    narrator = _safe_dict(audio_cast.get("narrator", {}))
    characters = _safe_list(audio_cast.get("characters", []))
    contributors: List[Dict[str, Any]] = []

    def add_contributor(profile_id: str, role: str, character_name: str = ""):
        profile = get_voice_profile(profile_id)
        if not profile:
            return
        owner_key = _normalize_str(profile.get("owner_person_id")) or _normalize_str(profile.get("owner_person_name")) or _normalize_str(profile.get("id"))
        if not owner_key:
            return
        credited_name = _normalize_str(profile.get("credited_name")) or _normalize_str(profile.get("owner_person_name")) or _normalize_str(profile.get("display_name"))
        existing = next((item for item in contributors if _normalize_str(item.get("owner_key")) == owner_key), None)
        role_entry = {
            "role": role,
            "character_name": character_name,
            "voice_profile_id": _normalize_str(profile.get("id")),
            "display_name": _normalize_str(profile.get("display_name")),
            "variation_policy": _safe_dict(profile.get("voice_variation_policy", {})),
        }
        if existing:
            existing["voice_roles"].append(role_entry)
            return
        contributors.append({
            "owner_key": owner_key,
            "owner_person_id": _normalize_str(profile.get("owner_person_id")),
            "owner_person_name": _normalize_str(profile.get("owner_person_name")),
            "credited_name": credited_name,
            "credit_visibility": _normalize_str(profile.get("credit_visibility")) or "product_and_website",
            "voice_roles": [role_entry],
        })

    narrator_profile_id = _normalize_str(narrator.get("voice_profile_id"))
    if narrator_profile_id:
        add_contributor(narrator_profile_id, "narrator")

    for row in characters:
        item = _safe_dict(row)
        profile_id = _normalize_str(item.get("voice_profile_id"))
        if profile_id:
            add_contributor(profile_id, "character", _normalize_str(item.get("name")))

    return {
        "audio_cast": audio_cast,
        "audio_contributors": contributors,
        "audio_credit_lines": [
            {
                "credited_name": item.get("credited_name"),
                "roles": [
                    {"role": role.get("role"), "character_name": role.get("character_name", "")}
                    for role in _safe_list(item.get("voice_roles"))
                ],
            }
            for item in contributors
        ],
    }


def _check_required_fields(commercial: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"field": field, "required": True, "ok": _has_value(commercial.get(field)), "value": commercial.get(field)} for field in REQUIRED_COMMERCIAL_FIELDS]


def _check_recommended_fields(commercial: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"field": field, "required": False, "ok": _has_value(commercial.get(field)), "value": commercial.get(field)} for field in RECOMMENDED_COMMERCIAL_FIELDS]


def _extract_output_presence(outputs: Dict[str, Any]) -> Dict[str, Any]:
    covers = _safe_dict(outputs.get("covers", {}))
    epub = _safe_dict(outputs.get("epub", {}))
    audiobook = _safe_dict(outputs.get("audiobook", {}))
    video = _safe_dict(outputs.get("video", {}))
    guide = outputs.get("guide")
    return {
        "covers": bool(covers and covers.get("file_path")),
        "epub": any(bool(_safe_dict(item).get("file_path")) for item in epub.values()),
        "audiobook": any(bool(_safe_dict(item).get("file_path")) for item in audiobook.values()),
        "video": any(bool(_safe_dict(item).get("file_path")) for item in video.values()),
        "guide": bool(guide),
    }


def _build_readiness(required_checks: List[Dict[str, Any]], recommended_checks: List[Dict[str, Any]], output_presence: Dict[str, Any]) -> Dict[str, Any]:
    required_fields_ok = all(item["ok"] for item in required_checks)
    required_outputs_ok = all(bool(output_presence.get(name)) for name in REQUIRED_OUTPUT_GROUPS)
    missing_required_fields = [item["field"] for item in required_checks if not item["ok"]]
    missing_required_outputs = [name for name in REQUIRED_OUTPUT_GROUPS if not output_presence.get(name)]
    missing_recommended_fields = [item["field"] for item in recommended_checks if not item["ok"]]
    required_ok = required_fields_ok and required_outputs_ok
    recommended_ok = len(missing_recommended_fields) == 0
    status = "green" if required_ok and recommended_ok else "yellow" if required_ok else "red"
    label = "Pronto para publicar" if status == "green" else "Quase pronto" if status == "yellow" else "Não pronto"
    score = 0
    total = len(required_checks) + len(recommended_checks) + len(REQUIRED_OUTPUT_GROUPS) + len(OPTIONAL_OUTPUT_GROUPS)
    for item in required_checks:
        if item["ok"]:
            score += 1
    for item in recommended_checks:
        if item["ok"]:
            score += 1
    for name in REQUIRED_OUTPUT_GROUPS:
        if output_presence.get(name):
            score += 1
    for name in OPTIONAL_OUTPUT_GROUPS:
        if output_presence.get(name):
            score += 1
    percent = round((score / total) * 100) if total else 0
    return {
        "ready": status == "green",
        "status": status,
        "label": label,
        "score_percent": percent,
        "required_fields_ok": required_fields_ok,
        "required_outputs_ok": required_outputs_ok,
        "missing_required_fields": missing_required_fields,
        "missing_required_outputs": missing_required_outputs,
        "missing_recommended_fields": missing_recommended_fields,
    }


def _build_public_assets(project_id: str | None, ip_slug: str | None) -> Dict[str, Any]:
    def _first(query: Dict[str, Any]) -> Dict[str, Any] | None:
        items = get_assets(query)
        return items[0] if items else None
    def _many(query: Dict[str, Any]) -> List[Dict[str, Any]]:
        return get_assets(query)
    def _url(asset: Dict[str, Any] | None) -> str | None:
        if not asset:
            return None
        return resolve_cdn_url(asset.get("storage_path", ""), asset.get("version"))
    def _urls(items: List[Dict[str, Any]]) -> List[str]:
        return [resolve_cdn_url(item.get("storage_path", ""), item.get("version")) for item in items if item.get("storage_path")]

    studio_logo = _first({"asset_type": "studio_logo", "status": "published", "is_primary": True})
    ip_primary_logo = _first({"ip_slug": ip_slug, "asset_type": "ip_logo", "status": "published", "is_primary": True})
    ip_secondary_logos = _many({"ip_slug": ip_slug, "asset_type": "ip_logo", "status": "published"})
    cover = _first({"project_id": project_id, "asset_type": "cover", "status": "published", "is_primary": True})
    hero = _first({"ip_slug": ip_slug, "asset_type": "hero_background", "status": "published", "is_primary": True})
    gallery = _many({"project_id": project_id, "asset_type": "gallery_image", "status": "published"})
    ornaments = _many({"ip_slug": ip_slug, "asset_type": "ornament", "status": "published"})
    badges = _many({"ip_slug": ip_slug, "asset_type": "badge", "status": "published"})
    promo = _many({"project_id": project_id, "asset_type": "promo_banner", "status": "published"})
    trailer_thumbnail = _first({"project_id": project_id, "asset_type": "trailer_thumbnail", "status": "published", "is_primary": True})
    character_cards = _many({"ip_slug": ip_slug, "asset_type": "character_card", "status": "published"})
    background_textures = _many({"ip_slug": ip_slug, "asset_type": "background_texture", "status": "published"})
    social_cards = _many({"project_id": project_id, "asset_type": "social_card", "status": "published"})
    campaign_visuals = _many({"ip_slug": ip_slug, "asset_type": "campaign_visual", "status": "published"})

    return {
        "studio_logo": _url(studio_logo),
        "primary_logo": _url(ip_primary_logo),
        "secondary_logos": _urls(ip_secondary_logos),
        "cover": _url(cover),
        "hero_background": _url(hero),
        "gallery": _urls(gallery),
        "ornaments": _urls(ornaments),
        "badges": _urls(badges),
        "promo_banners": _urls(promo),
        "trailer_thumbnail": _url(trailer_thumbnail),
        "character_cards": _urls(character_cards),
        "background_textures": _urls(background_textures),
        "social_cards": _urls(social_cards),
        "campaign_visuals": _urls(campaign_visuals),
    }


def build_publication_package(project: Dict[str, Any]) -> Dict[str, Any]:
    saga_id = _normalize_str(project.get("saga_slug", "baribudos")) or "baribudos"
    runtime = load_saga_runtime(saga_id)
    metadata = _safe_dict(runtime.get("metadata", {}))
    resolved = _safe_dict(runtime.get("resolved", {}))
    commercial = _safe_dict(project.get("commercial", {}))
    outputs = _safe_dict(project.get("outputs", {}))
    continuity = _safe_dict(project.get("continuity", {}))
    typography = _resolve_typography(project)
    audio_credit_block = _resolve_audio_credits(project)

    required_checks = _check_required_fields(commercial)
    recommended_checks = _check_recommended_fields(commercial)
    output_presence = _extract_output_presence(outputs)
    readiness = _build_readiness(required_checks, recommended_checks, output_presence)

    project_id = _normalize_str(project.get("id"))
    ip_slug = _normalize_str(project.get("saga_slug")) or saga_id
    language = _normalize_str(project.get("language")) or runtime.get("default_language", "pt-PT")

    public_assets = _build_public_assets(project_id=project_id or None, ip_slug=ip_slug or None)
    branding_resolution = resolve_brand_assets(context="product_page", ip_slug=ip_slug or None, project_id=project_id or None, language=language or None, channel="website")

    website_contract = {
        "project_id": project_id,
        "project_slug": _normalize_str(project.get("slug")) or project_id,
        "ip_slug": ip_slug,
        "ip_name": _normalize_str(project.get("saga_name")) or runtime.get("name", ""),
        "series_name": metadata.get("series_name", ""),
        "language": language,
        "title": _normalize_str(project.get("title")),
        "description": metadata.get("description", ""),
        "formats": [name for name, ok in output_presence.items() if ok],
        "price": commercial.get("price", ""),
        "currency": commercial.get("currency", "EUR"),
        "variant_id": f"{project_id}:website:{language}:default" if project_id else "",
        "channel": "website",
        "seo": {
            "title": _normalize_str(project.get("title")),
            "description": commercial.get("blurb") or metadata.get("description", ""),
            "keywords": _safe_list(commercial.get("keywords", [])),
            "canonical_url": "",
            "og_image": public_assets.get("cover") or public_assets.get("hero_background") or "",
        },
        "assets": public_assets,
        "characters": _safe_list(runtime.get("main_characters", [])),
        "themes": _safe_list(metadata.get("themes", [])),
        "values": _safe_list(metadata.get("values", [])),
        "authors": [metadata.get("author_default")] if metadata.get("author_default") else [],
        "badges": _safe_list(public_assets.get("badges", [])),
        "video_trailer": public_assets.get("trailer_thumbnail", ""),
        "buy_links": [],
        "typography": typography,
        "continuity": continuity,
        "audio_credits": audio_credit_block.get("audio_credit_lines", []),
    }

    return {
        "generated_at": now_iso(),
        "project": {
            "id": project.get("id"),
            "title": project.get("title"),
            "slug": project.get("slug", ""),
            "language": project.get("language"),
            "output_languages": project.get("output_languages", []),
            "saga_slug": project.get("saga_slug"),
            "saga_name": project.get("saga_name"),
            "created_by": project.get("created_by"),
            "created_by_name": project.get("created_by_name"),
            "status": project.get("status"),
            "editorial_status": project.get("editorial_status"),
            "ready_for_publish": bool(project.get("ready_for_publish", False)),
            "project_mode": project.get("project_mode", "official"),
            "hidden_universe_name": project.get("hidden_universe_name", ""),
            "hidden_saga_name": project.get("hidden_saga_name", ""),
        },
        "runtime": {
            "slug": runtime.get("slug", ""),
            "name": runtime.get("name", ""),
            "default_language": runtime.get("default_language", "pt-PT"),
            "output_languages": runtime.get("output_languages", []),
            "validation": runtime.get("validation", {}),
        },
        "editorial": {
            "author_default": metadata.get("author_default", ""),
            "producer": metadata.get("producer", ""),
            "tagline": metadata.get("tagline", ""),
            "mission": metadata.get("mission", ""),
            "target_age": metadata.get("target_age", ""),
            "series_name": metadata.get("series_name", ""),
            "genre": metadata.get("genre", ""),
            "description": metadata.get("description", ""),
            "resolved_series_name": resolved.get("series_name", ""),
            "resolved_final_phrase": resolved.get("final_phrase_rule", ""),
            "typography": typography,
            "continuity": continuity,
            "audio_cast": audio_credit_block.get("audio_cast", {}),
            "audio_contributors": audio_credit_block.get("audio_contributors", []),
            "audio_credit_lines": audio_credit_block.get("audio_credit_lines", []),
        },
        "commercial": {
            "internal_code": commercial.get("internal_code", ""),
            "isbn": commercial.get("isbn", ""),
            "asin": commercial.get("asin", ""),
            "price": commercial.get("price", ""),
            "currency": commercial.get("currency", "EUR"),
            "collection_seal": commercial.get("collection_seal", ""),
            "marketplaces": commercial.get("marketplaces", []),
            "commercial_status": commercial.get("commercial_status", "draft"),
            "channels": commercial.get("channels", []),
            "keywords": commercial.get("keywords", []),
            "subtitle": commercial.get("subtitle", ""),
            "blurb": commercial.get("blurb", ""),
        },
        "assets": {
            "cover_image": project.get("cover_image", ""),
            "illustration_path": project.get("illustration_path", ""),
            "brand_assets": runtime.get("brand_assets", {}),
            "palette": runtime.get("palette", {}),
            "public": public_assets,
            "branding_resolution": branding_resolution,
        },
        "outputs": outputs,
        "checks": {
            "required_fields": required_checks,
            "recommended_fields": recommended_checks,
            "output_presence": output_presence,
            "readiness": readiness,
        },
        "website_payload": website_contract,
    }
