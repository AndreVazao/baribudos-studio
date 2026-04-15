from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from studio_core.core.models import now_iso
from studio_core.core.storage import get_json_item, update_json_item
from studio_core.services.production_readiness_service import build_production_readiness
from studio_core.services.publication_package_service import build_publication_package
from studio_core.services.publication_policy_service import evaluate_project_publication_policy

PROJECTS_FILE = "data/projects.json"
FREEZE_VERSION = "v7"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _checksum(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_project(project_id: str) -> Dict[str, Any] | None:
    return get_json_item(PROJECTS_FILE, project_id)


def build_freeze_snapshot(project: Dict[str, Any], user_name: str = "", user_role: str = "") -> Dict[str, Any]:
    package = build_publication_package(project)
    readiness = build_production_readiness(project)
    freeze_time = now_iso()
    project_with_package = {
        **project,
        "publication_package": package,
        "publication_package_frozen_at": freeze_time,
    }
    policy = evaluate_project_publication_policy(project_with_package)

    snapshot_core = {
        "freeze_version": FREEZE_VERSION,
        "frozen_at": freeze_time,
        "project_id": _text(project.get("id")),
        "project_title": _text(project.get("title")),
        "project_language": _text(project.get("language")),
        "ready_for_publish": bool(project.get("ready_for_publish")),
        "publication_package_frozen_at": freeze_time,
        "frozen_by": {
            "user_name": _text(user_name),
            "user_role": _text(user_role),
        },
        "readiness": {
            "label": _text(readiness.get("label")),
            "ratio": readiness.get("ratio", 0),
            "completed": readiness.get("completed", 0),
            "total": readiness.get("total", 0),
            "package_readiness": _safe_dict(readiness.get("package_readiness")),
        },
        "policy": policy,
        "package": package,
    }

    return {
        **snapshot_core,
        "package_checksum": _checksum(package),
        "freeze_checksum": _checksum(snapshot_core),
    }


def freeze_publication_package_operationally(project_id: str, user_name: str = "", user_role: str = "") -> Dict[str, Any]:
    project = _load_project(project_id)
    if not project:
        raise ValueError("project_not_found")

    if not bool(project.get("ready_for_publish", False)):
        raise ValueError("project_not_ready_for_publish")

    snapshot = build_freeze_snapshot(project, user_name=user_name, user_role=user_role)
    contract = _safe_dict(_safe_dict(snapshot.get("policy")).get("contract"))
    if not bool(contract.get("required_ok", False)):
        raise ValueError("website_contract_not_ready")

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "publication_package": snapshot.get("package", {}),
            "publication_package_frozen_at": snapshot.get("frozen_at", now_iso()),
            "publication_package_freeze": {
                "freeze_version": snapshot.get("freeze_version", FREEZE_VERSION),
                "frozen_at": snapshot.get("frozen_at", now_iso()),
                "package_checksum": snapshot.get("package_checksum", ""),
                "freeze_checksum": snapshot.get("freeze_checksum", ""),
                "frozen_by": snapshot.get("frozen_by", {}),
                "policy": snapshot.get("policy", {}),
                "readiness": snapshot.get("readiness", {}),
            },
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "project_id": project_id,
        "publication_package": updated.get("publication_package", {}),
        "publication_package_frozen_at": updated.get("publication_package_frozen_at", ""),
        "publication_package_freeze": _safe_dict(updated.get("publication_package_freeze")),
    }
