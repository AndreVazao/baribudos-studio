from __future__ import annotations

from typing import Any, Dict, List

from studio_core.services.publication_payload_builder import build_store_payload


REQUIRED_FIELDS = [
    "project_id",
    "project_slug",
    "ip_slug",
    "ip_name",
    "series_name",
    "language",
    "title",
    "description",
    "formats",
    "price",
    "currency",
    "seo",
    "assets",
    "variant_id",
    "channel",
]

RECOMMENDED_FIELDS = [
    "characters",
    "themes",
    "values",
    "authors",
    "badges",
    "video_trailer",
    "buy_links",
]

REQUIRED_ASSET_FIELDS = [
    "cover",
]

RECOMMENDED_ASSET_FIELDS = [
    "primary_logo",
    "secondary_logos",
    "hero_background",
    "gallery",
    "ornaments",
    "badges",
    "promo_banners",
]


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _has_value(value: Any) -> bool:
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return value is not None and str(value).strip() != ""


def validate_store_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = _safe_dict(payload)
    assets = _safe_dict(payload.get("assets"))
    seo = _safe_dict(payload.get("seo"))

    required_checks = []
    for field in REQUIRED_FIELDS:
        required_checks.append({
            "field": field,
            "ok": _has_value(payload.get(field)),
            "value": payload.get(field),
        })

    recommended_checks = []
    for field in RECOMMENDED_FIELDS:
        recommended_checks.append({
            "field": field,
            "ok": _has_value(payload.get(field)),
            "value": payload.get(field),
        })

    required_asset_checks = []
    for field in REQUIRED_ASSET_FIELDS:
        required_asset_checks.append({
            "field": f"assets.{field}",
            "ok": _has_value(assets.get(field)),
            "value": assets.get(field),
        })

    recommended_asset_checks = []
    for field in RECOMMENDED_ASSET_FIELDS:
        recommended_asset_checks.append({
            "field": f"assets.{field}",
            "ok": _has_value(assets.get(field)),
            "value": assets.get(field),
        })

    seo_checks = [
        {"field": "seo.title", "ok": _has_value(seo.get("title")), "value": seo.get("title")},
        {"field": "seo.description", "ok": _has_value(seo.get("description")), "value": seo.get("description")},
        {"field": "seo.keywords", "ok": _has_value(seo.get("keywords")), "value": seo.get("keywords")},
        {"field": "seo.og_image", "ok": _has_value(seo.get("og_image")), "value": seo.get("og_image")},
    ]

    missing_required = [item["field"] for item in required_checks if not item["ok"]]
    missing_required_assets = [item["field"] for item in required_asset_checks if not item["ok"]]
    missing_recommended = [item["field"] for item in recommended_checks if not item["ok"]]
    missing_recommended_assets = [item["field"] for item in recommended_asset_checks if not item["ok"]]
    missing_seo = [item["field"] for item in seo_checks if not item["ok"]]

    required_ok = len(missing_required) == 0 and len(missing_required_assets) == 0
    seo_ok = len(missing_seo) == 0

    if required_ok and seo_ok:
        status = "green"
        label = "Website contract pronto"
    elif required_ok:
        status = "yellow"
        label = "Website contract quase pronto"
    else:
        status = "red"
        label = "Website contract incompleto"

    total = (
        len(required_checks)
        + len(recommended_checks)
        + len(required_asset_checks)
        + len(recommended_asset_checks)
        + len(seo_checks)
    )

    score = 0
    for group in [required_checks, recommended_checks, required_asset_checks, recommended_asset_checks, seo_checks]:
        for item in group:
            if item["ok"]:
                score += 1

    score_percent = round((score / total) * 100) if total else 0

    return {
        "ok": True,
        "status": status,
        "label": label,
        "score_percent": score_percent,
        "required_ok": required_ok,
        "seo_ok": seo_ok,
        "missing_required_fields": missing_required,
        "missing_required_assets": missing_required_assets,
        "missing_recommended_fields": missing_recommended,
        "missing_recommended_assets": missing_recommended_assets,
        "missing_seo_fields": missing_seo,
        "checks": {
            "required_fields": required_checks,
            "recommended_fields": recommended_checks,
            "required_assets": required_asset_checks,
            "recommended_assets": recommended_asset_checks,
            "seo": seo_checks,
        },
        "payload": payload,
    }


def validate_project_website_contract(project: Dict[str, Any]) -> Dict[str, Any]:
    payload = build_store_payload(project)
    result = validate_store_payload(payload)
    result["project_id"] = project.get("id")
    return result
