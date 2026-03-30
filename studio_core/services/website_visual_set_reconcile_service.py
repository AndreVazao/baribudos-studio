from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.storage import list_json_items
from studio_core.services.website_visual_set_service import get_website_visual_sets_status

SAGA_VISUAL_SETS_FILE = "data/saga_visual_sets.json"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def get_visual_set_reconcile_report() -> Dict[str, Any]:
    local_items = list_json_items(SAGA_VISUAL_SETS_FILE)
    website_payload = get_website_visual_sets_status()
    website_items = _safe_list(website_payload.get("items"))

    website_by_id = {
        _normalize_text(item.get("id")): item
        for item in website_items
        if _normalize_text(item.get("id"))
    }

    report_items: List[Dict[str, Any]] = []

    for item in local_items:
        item_id = _normalize_text(item.get("id"))
        website_item = website_by_id.get(item_id)

        local_signature = {
            "saga_slug": _normalize_text(item.get("saga_slug")),
            "display_name": _normalize_text(item.get("display_name")),
            "active": bool(item.get("active", False)),
            "version": int(item.get("version") or 0),
            "source_of_truth": _normalize_text(item.get("source_of_truth")),
            "slots_count": len(_safe_dict(item.get("slots"))),
            "rotation_keys": sorted(list(_safe_dict(item.get("rotation_policy")).keys())),
        }

        website_signature = {
            "saga_slug": _normalize_text((website_item or {}).get("saga_slug")),
            "display_name": _normalize_text((website_item or {}).get("display_name")),
            "active": bool((website_item or {}).get("active", False)),
            "version": int((website_item or {}).get("version") or 0),
            "source_of_truth": _normalize_text((website_item or {}).get("source_of_truth")),
            "slots_count": len(_safe_dict((website_item or {}).get("slots"))),
            "rotation_keys": sorted(list(_safe_dict((website_item or {}).get("rotation_policy")).keys())),
        }

        status = "missing_on_website"
        if website_item:
            status = "in_sync" if local_signature == website_signature else "diverged"

        report_items.append({
            "id": item_id,
            "local": local_signature,
            "website": website_signature if website_item else None,
            "status": status,
        })

    orphan_website_items = [
        item for item in website_items
        if _normalize_text(item.get("id")) not in {_normalize_text(local.get("id")) for local in local_items}
    ]

    return {
        "ok": True,
        "local_count": len(local_items),
        "website_count": len(website_items),
        "report": report_items,
        "orphans_on_website": orphan_website_items,
    }
