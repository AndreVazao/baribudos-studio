from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from studio_core.core.config import resolve_storage_path


REGISTRY_PATH = resolve_storage_path("editorial/assets_registry.json")

VALID_STATUSES = {"draft", "approved", "published", "archived"}


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _normalize_status(value: Any) -> str:
    status = _safe_str(value).lower() or "draft"
    return status if status in VALID_STATUSES else "draft"


def _load_registry() -> List[Dict[str, Any]]:
    if not REGISTRY_PATH.exists():
        return []
    try:
        return _safe_list(json.loads(REGISTRY_PATH.read_text(encoding="utf-8")))
    except Exception:
        return []


def _save_registry(data: List[Dict[str, Any]]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _match_filters(asset: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    for key, value in filters.items():
        if value is None:
            continue
        if asset.get(key) != value:
            return False
    return True


def _sort_assets(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        items,
        key=lambda x: (
            -_safe_int(x.get("is_primary", False), 0),
            _safe_int(x.get("priority", 0), 0),
            -_safe_int(x.get("version", 1), 1),
            _safe_str(x.get("updated_at")),
        ),
    )


def _identity_group(asset: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "project_id": asset.get("project_id"),
        "ip_slug": asset.get("ip_slug"),
        "publication_id": asset.get("publication_id"),
        "variant_id": asset.get("variant_id"),
        "asset_type": asset.get("asset_type"),
        "context": asset.get("context"),
        "language": asset.get("language"),
    }


def _same_group(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    group_a = _identity_group(a)
    group_b = _identity_group(b)
    return group_a == group_b


def _next_version(registry: List[Dict[str, Any]], payload: Dict[str, Any]) -> int:
    versions = [
        _safe_int(item.get("version", 1), 1)
        for item in registry
        if _same_group(item, payload)
    ]
    return (max(versions) + 1) if versions else 1


def _normalize_asset_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _safe_dict(payload)

    normalized = {
        "project_id": data.get("project_id"),
        "ip_slug": _safe_str(data.get("ip_slug")),
        "series_name": data.get("series_name"),
        "publication_id": data.get("publication_id"),
        "variant_id": data.get("variant_id"),
        "asset_type": _safe_str(data.get("asset_type")),
        "context": _safe_str(data.get("context")),
        "language": data.get("language"),
        "version": _safe_int(data.get("version", 1), 1),
        "is_primary": bool(data.get("is_primary", False)),
        "priority": _safe_int(data.get("priority", 0), 0),
        "width": data.get("width"),
        "height": data.get("height"),
        "mime_type": _safe_str(data.get("mime_type")),
        "file_size": data.get("file_size"),
        "url": _safe_str(data.get("url")),
        "storage_path": _safe_str(data.get("storage_path")),
        "status": _normalize_status(data.get("status")),
        "created_at": data.get("created_at") or _now_iso(),
        "updated_at": data.get("updated_at") or _now_iso(),
        "published_at": data.get("published_at"),
    }

    if normalized["status"] == "published" and not normalized["published_at"]:
        normalized["published_at"] = _now_iso()

    return normalized


def _unset_primary_for_group(
    registry: List[Dict[str, Any]],
    asset: Dict[str, Any],
) -> None:
    for item in registry:
        if item.get("asset_id") == asset.get("asset_id"):
            continue
        if not _same_group(item, asset):
            continue
        if bool(item.get("is_primary", False)):
            item["is_primary"] = False
            item["updated_at"] = _now_iso()


def register_asset(payload: Dict[str, Any]) -> Dict[str, Any]:
    registry = _load_registry()

    normalized_input = _normalize_asset_payload(payload)
    normalized_input["version"] = _next_version(registry, normalized_input)

    asset = {
        "asset_id": str(uuid.uuid4()),
        **normalized_input,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }

    if asset["status"] == "published" and not asset.get("published_at"):
        asset["published_at"] = _now_iso()

    if asset.get("is_primary", False):
        _unset_primary_for_group(registry, asset)

    registry.append(asset)
    _save_registry(registry)
    return asset


def update_asset(asset_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    registry = _load_registry()
    updated_asset: Optional[Dict[str, Any]] = None

    for index, item in enumerate(registry):
        if item.get("asset_id") != asset_id:
            continue

        merged = {
            **item,
            **_safe_dict(payload),
            "asset_id": item.get("asset_id"),
            "created_at": item.get("created_at"),
            "updated_at": _now_iso(),
        }

        normalized = _normalize_asset_payload(merged)
        normalized["asset_id"] = item.get("asset_id")
        normalized["created_at"] = item.get("created_at")
        normalized["updated_at"] = _now_iso()

        if normalized["status"] == "published" and not normalized.get("published_at"):
            normalized["published_at"] = _now_iso()

        registry[index] = normalized
        updated_asset = normalized
        break

    if not updated_asset:
        return None

    if updated_asset.get("is_primary", False):
        _unset_primary_for_group(registry, updated_asset)

    _save_registry(registry)
    return updated_asset


def publish_asset(asset_id: str) -> Optional[Dict[str, Any]]:
    registry = _load_registry()
    published_asset: Optional[Dict[str, Any]] = None

    for item in registry:
        if item.get("asset_id") != asset_id:
            continue

        item["status"] = "published"
        item["published_at"] = _now_iso()
        item["updated_at"] = _now_iso()
        published_asset = item
        break

    if not published_asset:
        return None

    if published_asset.get("is_primary", False):
        _unset_primary_for_group(registry, published_asset)

    _save_registry(registry)
    return published_asset


def archive_asset(asset_id: str) -> Optional[Dict[str, Any]]:
    registry = _load_registry()

    for item in registry:
        if item.get("asset_id") != asset_id:
            continue
        item["status"] = "archived"
        item["is_primary"] = False
        item["updated_at"] = _now_iso()
        _save_registry(registry)
        return item

    return None


def rollback_asset(asset_id: str) -> Optional[Dict[str, Any]]:
    registry = _load_registry()
    target = next((item for item in registry if item.get("asset_id") == asset_id), None)
    if not target:
        return None

    group = _identity_group(target)

    for item in registry:
        if _identity_group(item) != group:
            continue
        item["is_primary"] = item.get("asset_id") == asset_id
        if item.get("asset_id") == asset_id:
            item["status"] = "published"
            if not item.get("published_at"):
                item["published_at"] = _now_iso()
        item["updated_at"] = _now_iso()

    _save_registry(registry)
    return next((item for item in registry if item.get("asset_id") == asset_id), None)


def get_assets(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    registry = _load_registry()
    result = [item for item in registry if _match_filters(item, filters)]
    return _sort_assets(result)


def get_asset_by_id(asset_id: str) -> Optional[Dict[str, Any]]:
    registry = _load_registry()
    for item in registry:
        if item.get("asset_id") == asset_id:
            return item
    return None


def get_primary_asset(filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    items = get_assets({**filters, "is_primary": True})
    return items[0] if items else None


def build_ip_asset_manifest(ip_slug: str) -> Dict[str, Any]:
    primary_logo = get_primary_asset({
        "ip_slug": ip_slug,
        "asset_type": "ip_logo",
        "status": "published",
    })

    secondary_logos = get_assets({
        "ip_slug": ip_slug,
        "asset_type": "ip_logo",
        "status": "published",
    })

    hero_background = get_primary_asset({
        "ip_slug": ip_slug,
        "asset_type": "hero_background",
        "status": "published",
    })

    gallery = get_assets({
        "ip_slug": ip_slug,
        "asset_type": "gallery_image",
        "status": "published",
    })

    ornaments = get_assets({
        "ip_slug": ip_slug,
        "asset_type": "ornament",
        "status": "published",
    })

    badges = get_assets({
        "ip_slug": ip_slug,
        "asset_type": "badge",
        "status": "published",
    })

    promo_banners = get_assets({
        "ip_slug": ip_slug,
        "asset_type": "promo_banner",
        "status": "published",
    })

    return {
        "ok": True,
        "ip_slug": ip_slug,
        "assets": {
            "primary_logo": primary_logo,
            "secondary_logos": secondary_logos,
            "hero_background": hero_background,
            "gallery": gallery,
            "ornaments": ornaments,
            "badges": badges,
            "promo_banners": promo_banners,
        },
    }


def build_context_asset_manifest(context: str, ip_slug: str | None = None) -> Dict[str, Any]:
    base_filters = {
        "context": context,
        "status": "published",
    }

    if ip_slug:
        base_filters["ip_slug"] = ip_slug

    primary_logo = get_primary_asset({
        **base_filters,
        "asset_type": "ip_logo" if ip_slug else "studio_logo",
    })

    hero_background = get_primary_asset({
        **base_filters,
        "asset_type": "hero_background",
    })

    decorative_assets = get_assets({
        **base_filters,
        "asset_type": "ornament",
    })

    campaign_assets = get_assets({
        **base_filters,
        "asset_type": "campaign_visual",
    })

    return {
        "ok": True,
        "context": context,
        "ip_slug": ip_slug,
        "assets": {
            "primary_logo": primary_logo,
            "secondary_logo": None,
            "hero_background": hero_background,
            "decorative_assets": decorative_assets,
            "campaign_assets": campaign_assets,
        },
    }


def build_project_asset_manifest(project_id: str) -> Dict[str, Any]:
    cover = get_primary_asset({
        "project_id": project_id,
        "asset_type": "cover",
        "status": "published",
    })

    hero_background = get_primary_asset({
        "project_id": project_id,
        "asset_type": "hero_background",
        "status": "published",
    })

    gallery = get_assets({
        "project_id": project_id,
        "asset_type": "gallery_image",
        "status": "published",
    })

    trailer_thumbnail = get_primary_asset({
        "project_id": project_id,
        "asset_type": "trailer_thumbnail",
        "status": "published",
    })

    promo_banners = get_assets({
        "project_id": project_id,
        "asset_type": "promo_banner",
        "status": "published",
    })

    return {
        "ok": True,
        "project_id": project_id,
        "assets": {
            "cover": cover,
            "hero_background": hero_background,
            "gallery": gallery,
            "trailer_thumbnail": trailer_thumbnail,
            "promo_banners": promo_banners,
        },
}
