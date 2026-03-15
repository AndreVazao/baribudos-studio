from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import append_json_item, read_json, update_json_item
from studio_core.services.factory_service import run_factory
from studio_core.services.project_integrity_service import audit_project_integrity
from studio_core.services.publication_package_service import build_publication_package
from studio_core.services.publishing_service import validate_project_publishability
from studio_core.services.saga_runtime_service import load_saga_runtime

PROJECTS_FILE = "data/projects.json"
USERS_FILE = "data/users.json"
SMOKE_RESULTS_FILE = "data/smoke_results.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _find_user_by_name(name: str) -> Dict[str, Any] | None:
    users = read_json(USERS_FILE, [])
    for user in users:
        if str(user.get("name", "")).strip().lower() == str(name or "").strip().lower():
            return user
    return None


def _find_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")).strip() == str(project_id).strip():
            return project
    return None


def _collect_output_files(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    outputs = _safe_dict(project.get("outputs", {}))
    result: List[Dict[str, Any]] = []

    covers = _safe_dict(outputs.get("covers", {}))
    if covers.get("file_path"):
        result.append({"group": "covers", "language": "", "file_path": covers.get("file_path")})
    if covers.get("badge_file_path"):
        result.append({"group": "covers", "language": "", "file_path": covers.get("badge_file_path")})

    for group in ["epub", "audiobook", "video"]:
        items = _safe_dict(outputs.get(group, {}))
        for language, item in items.items():
            item = _safe_dict(item)
            if item.get("file_path"):
                result.append({
                    "group": group,
                    "language": str(language),
                    "file_path": item.get("file_path"),
                })

    return result


def _paths_exist(file_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    checked = []
    for item in file_items:
        file_path = str(item.get("file_path", "")).strip()
        checked.append({
            **item,
            "exists": bool(file_path and Path(file_path).exists() and Path(file_path).is_file())
        })
    return checked


def _default_commercial_patch(project_id: str) -> Dict[str, Any]:
    return {
        "internal_code": f"SMOKE-{project_id[:8]}",
        "isbn": "9780000000001",
        "asin": "B0SMOKETEST",
        "price": "4.99",
        "currency": "EUR",
        "collection_seal": "Smoke Collection",
        "marketplaces": ["PT"],
        "commercial_status": "ready",
        "channels": ["amazon_kdp"],
        "keywords": ["smoke", "studio", "baribudos"],
        "subtitle": "Validação técnica",
        "blurb": "Projeto técnico gerado para validar o pipeline integral do Studio.",
    }


def _patch_project_commercial(project_id: str) -> Dict[str, Any]:
    patch = _default_commercial_patch(project_id)

    return update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "commercial": {
                **(_safe_dict(current.get("commercial", {}))),
                **patch,
            },
            "updated_at": now_iso(),
        }
    )


def run_system_smoke(project_id: str) -> Dict[str, Any]:
    project = _find_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    saga_slug = str(project.get("saga_slug", "baribudos")).strip() or "baribudos"
    runtime = load_saga_runtime(saga_slug)

    if not str(project.get("illustration_path", "")).strip():
        raise ValueError("Projeto sem illustration_path. O smoke test precisa de uma ilustração base.")

    factory_result = run_factory(project_id, {
        "createStory": True,
        "createCover": True,
        "createEpub": True,
        "createAudiobook": True,
        "createSeries": True,
        "createGuide": True,
        "languages": [str(project.get("language") or runtime.get("default_language") or "pt-PT").strip() or "pt-PT"],
    })

    patched_project = _patch_project_commercial(project_id)
    publication_package = build_publication_package(patched_project)
    integrity = audit_project_integrity(patched_project)
    publishability = validate_project_publishability(patched_project)

    file_items = _collect_output_files(patched_project)
    checked_files = _paths_exist(file_items)

    result = {
        "id": str(uuid4()),
        "project_id": project_id,
        "runtime_slug": runtime.get("slug", ""),
        "runtime_name": runtime.get("name", ""),
        "factory_summary": factory_result.get("summary", {}),
        "publication_readiness": _safe_dict(_safe_dict(publication_package.get("checks", {})).get("readiness", {})),
        "integrity": integrity,
        "publishability": publishability,
        "files": checked_files,
        "ok": (
            bool(_safe_dict(_safe_dict(publication_package.get("checks", {})).get("readiness", {})).get("status") in {"yellow", "green"})
            and integrity.get("integrity_ok", False)
            and all(item.get("exists", False) for item in checked_files)
        ),
        "created_at": now_iso(),
    }

    append_json_item(SMOKE_RESULTS_FILE, result)
    return result
