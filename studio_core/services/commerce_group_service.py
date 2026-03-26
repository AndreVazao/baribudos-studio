from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import append_json_item, list_json_items, read_json, remove_json_item, update_json_item, write_json

COMMERCE_GROUPS_FILE = "data/commerce_groups.json"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _default_item(item: Dict[str, Any], position: int = 0) -> Dict[str, Any]:
    return {
        "product_id": _normalize_text(item.get("product_id")),
        "slug": _normalize_text(item.get("slug")),
        "title": _normalize_text(item.get("title")),
        "type": _normalize_text(item.get("type")),
        "currency": _normalize_text(item.get("currency")) or "EUR",
        "price_cents": int(item.get("price_cents") or 0),
        "position": int(item.get("position") or position),
    }


def list_commerce_groups() -> Dict[str, Any]:
    groups = list_json_items(COMMERCE_GROUPS_FILE)
    return {
        "ok": True,
        "groups": groups,
        "count": len(groups),
    }


def create_commerce_group(payload: Dict[str, Any]) -> Dict[str, Any]:
    slug = _normalize_text(payload.get("slug"))
    name = _normalize_text(payload.get("name"))
    if not slug:
        raise ValueError("group_slug_missing")
    if not name:
        raise ValueError("group_name_missing")

    existing = list_json_items(COMMERCE_GROUPS_FILE)
    if any(_normalize_text(item.get("slug")) == slug for item in existing):
        raise ValueError("group_slug_exists")

    items = [_default_item(item, index) for index, item in enumerate(_safe_list(payload.get("items")))]
    currency = _normalize_text(payload.get("currency")) or "EUR"
    price_cents = int(payload.get("price_cents") or 0)

    group = {
        "id": str(uuid4()),
        "slug": slug,
        "name": name,
        "description": _normalize_text(payload.get("description")),
        "group_type": _normalize_text(payload.get("group_type")) or "bundle",
        "currency": currency,
        "price_cents": price_cents,
        "active": bool(payload.get("active", False)),
        "featured": bool(payload.get("featured", False)),
        "items": items,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "source_of_truth": "studio",
        "publish_state": {
            "website": {
                "published": False,
                "published_at": "",
                "last_result": {},
            }
        },
    }
    append_json_item(COMMERCE_GROUPS_FILE, group)
    return group


def update_commerce_group(group_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    def _updater(current: Dict[str, Any]) -> Dict[str, Any]:
        items = current.get("items", [])
        if "items" in payload:
            items = [_default_item(item, index) for index, item in enumerate(_safe_list(payload.get("items")))]

        return {
            **current,
            "name": _normalize_text(payload.get("name")) or current.get("name", ""),
            "description": _normalize_text(payload.get("description")) if "description" in payload else current.get("description", ""),
            "group_type": _normalize_text(payload.get("group_type")) or current.get("group_type", "bundle"),
            "currency": _normalize_text(payload.get("currency")) or current.get("currency", "EUR"),
            "price_cents": int(payload.get("price_cents")) if "price_cents" in payload and payload.get("price_cents") is not None else current.get("price_cents", 0),
            "active": bool(payload.get("active")) if "active" in payload else bool(current.get("active", False)),
            "featured": bool(payload.get("featured")) if "featured" in payload else bool(current.get("featured", False)),
            "items": items,
            "updated_at": now_iso(),
        }

    return update_json_item(COMMERCE_GROUPS_FILE, group_id, _updater)


def delete_commerce_group(group_id: str) -> Dict[str, Any]:
    return remove_json_item(COMMERCE_GROUPS_FILE, group_id)


def mark_commerce_group_publish_state(group_id: str, website_result: Dict[str, Any]) -> Dict[str, Any]:
    def _updater(current: Dict[str, Any]) -> Dict[str, Any]:
        return {
            **current,
            "publish_state": {
                **(current.get("publish_state") or {}),
                "website": {
                    "published": bool(website_result.get("ok", False)),
                    "published_at": now_iso(),
                    "last_result": website_result,
                },
            },
            "updated_at": now_iso(),
        }

    return update_json_item(COMMERCE_GROUPS_FILE, group_id, _updater)
