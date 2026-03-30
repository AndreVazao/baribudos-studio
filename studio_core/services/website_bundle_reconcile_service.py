from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.storage import list_json_items
from studio_core.services.website_bundle_service import get_website_bundles_status

COMMERCE_GROUPS_FILE = "data/commerce_groups.json"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def get_bundle_reconcile_report(limit: int = 100) -> Dict[str, Any]:
    local_groups = list_json_items(COMMERCE_GROUPS_FILE)
    website_payload = get_website_bundles_status(limit=max(1, min(int(limit), 100)))
    website_bundles = _safe_list(website_payload.get("bundles"))

    website_by_group_id = {
        _normalize_text(item.get("group_id")): item
        for item in website_bundles
        if _normalize_text(item.get("group_id"))
    }

    report_items: List[Dict[str, Any]] = []

    for group in local_groups:
        group_id = _normalize_text(group.get("id"))
        website_bundle = website_by_group_id.get(group_id)

        local_items = _safe_list(group.get("items"))
        website_items = _safe_list((website_bundle or {}).get("items"))

        local_signature = {
            "slug": _normalize_text(group.get("slug")),
            "name": _normalize_text(group.get("name")),
            "price_cents": int(group.get("price_cents") or 0),
            "currency": _normalize_text(group.get("currency")) or "EUR",
            "active": bool(group.get("active", False)),
            "featured": bool(group.get("featured", False)),
            "items_count": len(local_items),
        }

        website_signature = {
            "slug": _normalize_text((website_bundle or {}).get("slug")),
            "name": _normalize_text((website_bundle or {}).get("name")),
            "price_cents": int((website_bundle or {}).get("price_cents") or 0),
            "currency": _normalize_text((website_bundle or {}).get("currency")) or "EUR",
            "active": bool((website_bundle or {}).get("active", False)),
            "featured": bool((website_bundle or {}).get("featured", False)),
            "items_count": len(website_items),
        }

        status = "missing_on_website"
        if website_bundle:
            status = "in_sync" if local_signature == website_signature else "diverged"

        report_items.append({
            "group_id": group_id,
            "local": local_signature,
            "website": website_signature if website_bundle else None,
            "status": status,
            "publish_state": group.get("publish_state") or {},
        })

    orphan_website_bundles = [
        item for item in website_bundles
        if _normalize_text(item.get("group_id")) not in {_normalize_text(group.get("id")) for group in local_groups}
    ]

    return {
        "ok": True,
        "local_count": len(local_groups),
        "website_count": len(website_bundles),
        "report": report_items,
        "orphans_on_website": orphan_website_bundles,
    }
