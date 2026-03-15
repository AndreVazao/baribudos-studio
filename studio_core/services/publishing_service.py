from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.services.publication_package_service import build_publication_package


def _file_exists(value: str) -> bool:
    path = str(value or "").strip()
    if not path:
        return False
    try:
        return Path(path).exists() and Path(path).is_file()
    except Exception:
        return False


def publish_package(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(uuid4()),
        "project_id": str(payload.get("project_id", "")).strip(),
        "language": str(payload.get("language", "pt-PT")).strip(),
        "channel": str(payload.get("channel", "ebook")).strip(),
        "requested_by": str(payload.get("requested_by", "")).strip(),
        "notes": str(payload.get("notes", "")).strip(),
        "status": "published",
        "published_at": now_iso()
    }


def validate_project_publishability(project: Dict[str, Any]) -> Dict[str, Any]:
    package = build_publication_package(project)
    readiness = (package.get("checks") or {}).get("readiness", {}) or {}

    cover_path = str(project.get("cover_image", "")).strip()
    cover_ok = _file_exists(cover_path)

    epub_outputs = ((project.get("outputs") or {}).get("epub") or {})
    epub_ok = any(_file_exists((item or {}).get("file_path", "")) for item in epub_outputs.values())

    hard_failures = []
    if not readiness.get("ready", False):
        hard_failures.append("readiness_not_green")
    if not cover_ok:
        hard_failures.append("cover_file_missing")
    if not epub_ok:
        hard_failures.append("epub_file_missing")

    return {
        "ok": len(hard_failures) == 0,
        "hard_failures": hard_failures,
        "readiness": readiness,
        "package": package,
        "file_guards": {
            "cover_ok": cover_ok,
            "epub_ok": epub_ok,
        }
    }
