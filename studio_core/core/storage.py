from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List

from studio_core.core.config import APP_CONFIG, resolve_storage_path


DEFAULT_JSON_FILES: Dict[str, Any] = {
    "data/users.json": [],
    "data/projects.json": [],
    "data/settings.json": {},
    "data/sagas.json": [],
    "data/publications.json": [],
    "data/jobs.json": [],
    "data/sponsors.json": [],
    "data/assets.json": [],
    "data/voices.json": [],
}


def ensure_storage_structure() -> Dict[str, str]:
    folders = APP_CONFIG.folder_map()

    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)

    for relative_path, default_value in DEFAULT_JSON_FILES.items():
        full_path = resolve_storage_path(relative_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if not full_path.exists():
            write_json(relative_path, default_value)

    return {name: str(path) for name, path in folders.items()}


def _normalize_path(relative_path: str) -> Path:
    clean = str(relative_path).strip().lstrip("/\\")
    return resolve_storage_path(clean)


def read_json(relative_path: str, fallback: Any = None) -> Any:
    path = _normalize_path(relative_path)

    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json(relative_path: str, value: Any) -> Any:
    path = _normalize_path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return value


def list_json_items(relative_path: str) -> List[Dict[str, Any]]:
    data = read_json(relative_path, [])
    return data if isinstance(data, list) else []


def get_json_item(relative_path: str, item_id: str) -> Dict[str, Any] | None:
    items = list_json_items(relative_path)
    for item in items:
        if str(item.get("id", "")) == str(item_id):
            return item
    return None


def append_json_item(relative_path: str, item: Dict[str, Any]) -> Dict[str, Any]:
    items = list_json_items(relative_path)
    items.append(item)
    write_json(relative_path, items)
    return item


def update_json_item(
    relative_path: str,
    item_id: str,
    updater: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    items = list_json_items(relative_path)
    found = False
    updated_item: Dict[str, Any] | None = None
    new_items: List[Dict[str, Any]] = []

    for item in items:
        if str(item.get("id", "")) == str(item_id):
            updated_item = updater(item)
            new_items.append(updated_item)
            found = True
        else:
            new_items.append(item)

    if not found or updated_item is None:
        raise ValueError(f"Item não encontrado: {item_id}")

    write_json(relative_path, new_items)
    return updated_item


def upsert_json_item(
    relative_path: str,
    item_id: str,
    builder: Callable[[Dict[str, Any] | None], Dict[str, Any]],
) -> Dict[str, Any]:
    items = list_json_items(relative_path)
    found = False
    updated_item: Dict[str, Any] | None = None
    new_items: List[Dict[str, Any]] = []

    for item in items:
        if str(item.get("id", "")) == str(item_id):
            updated_item = builder(item)
            new_items.append(updated_item)
            found = True
        else:
            new_items.append(item)

    if not found:
        updated_item = builder(None)
        new_items.append(updated_item)

    write_json(relative_path, new_items)
    return updated_item


def remove_json_item(relative_path: str, item_id: str) -> Dict[str, bool]:
    items = list_json_items(relative_path)
    new_items = [item for item in items if str(item.get("id", "")) != str(item_id)]
    removed = len(new_items) != len(items)
    write_json(relative_path, new_items)
    return {"removed": removed}
