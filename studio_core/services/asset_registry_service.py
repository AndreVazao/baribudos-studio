import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from studio_core.core.config import resolve_storage_path
from studio_core.models.asset import Asset


REGISTRY_PATH = resolve_storage_path("editorial/assets_registry.json")


def _load_registry():
    if not REGISTRY_PATH.exists():
        return []
    import json
    return json.loads(REGISTRY_PATH.read_text())


def _save_registry(data):
    import json
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2))


def register_asset(payload: dict) -> dict:
    registry = _load_registry()

    asset_id = str(uuid.uuid4())

    asset = {
        "asset_id": asset_id,
        **payload,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "published_at": None
    }

    registry.append(asset)
    _save_registry(registry)

    return asset


def publish_asset(asset_id: str):
    registry = _load_registry()

    for a in registry:
        if a["asset_id"] == asset_id:
            a["status"] = "published"
            a["published_at"] = datetime.utcnow().isoformat()

    _save_registry(registry)


def get_assets(filters: dict) -> List[dict]:
    registry = _load_registry()

    result = []

    for a in registry:
        match = True
        for k, v in filters.items():
            if v is None:
                continue
            if a.get(k) != v:
                match = False
                break
        if match:
            result.append(a)

    return result
