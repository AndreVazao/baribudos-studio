from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.storage import append_json_item, list_json_items

PUBLICATIONS_FILE = "data/publications.json"


def list_publications() -> List[Dict[str, Any]]:
    return list_json_items(PUBLICATIONS_FILE)


def create_publication_record(payload: Dict[str, Any]) -> Dict[str, Any]:
    publication = {
        "id": str(uuid4()),
        "project_id": str(payload.get("project_id", "")).strip(),
        "language": str(payload.get("language", "pt-PT")).strip(),
        "channel": str(payload.get("channel", "ebook")).strip(),
        "status": str(payload.get("status", "queued")).strip(),
        "requested_by": str(payload.get("requested_by", "")).strip(),
        "notes": str(payload.get("notes", "")).strip(),
    }

    append_json_item(PUBLICATIONS_FILE, publication)
    return publication


def publish_package(payload: Dict[str, Any]) -> Dict[str, Any]:
    return create_publication_record({
        **payload,
        "status": "prepared"
    })
