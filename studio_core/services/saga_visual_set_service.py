from __future__ import annotations

from typing import Any, Dict

from studio_core.core.storage import list_json_items, update_json_item, write_json

SAGA_VISUAL_SETS_FILE = "data/saga_visual_sets.json"


def list_saga_visual_sets() -> Dict[str, Any]:
    items = list_json_items(SAGA_VISUAL_SETS_FILE)
    return {
        "ok": True,
        "items": items,
        "count": len(items),
    }


def replace_saga_visual_sets(payload: Dict[str, Any]) -> Dict[str, Any]:
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        raise ValueError("Payload inválido: 'items' deve ser uma lista.")

    write_json(SAGA_VISUAL_SETS_FILE, items)
    return {
        "ok": True,
        "items": items,
        "count": len(items),
    }


def update_saga_visual_set(item_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    if not str(item_id or "").strip():
        raise ValueError("ID inválido.")

    if not isinstance(patch, dict) or not patch:
        raise ValueError("Patch inválido.")

    def _updater(current: Dict[str, Any]) -> Dict[str, Any]:
        updated = dict(current)
        for key, value in patch.items():
            updated[key] = value
        return updated

    item = update_json_item(SAGA_VISUAL_SETS_FILE, item_id, _updater)
    return {
        "ok": True,
        "item": item,
    }
