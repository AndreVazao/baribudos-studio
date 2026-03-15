from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.models import now_iso
from studio_core.core.storage import ensure_storage_structure, read_json, write_json

USERS_FILE = "data/users.json"
PROJECTS_FILE = "data/projects.json"
IPS_FILE = "data/ip_registry.json"
SMOKE_RESULTS_FILE = "data/smoke_results.json"
PUBLICATIONS_FILE = "data/publications.json"
SETTINGS_FILE = "data/settings.json"
JOBS_FILE = "data/jobs.json"
SAGAS_FILE = "data/sagas.json"
SPONSORS_FILE = "data/sponsors.json"


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _ensure_json_list(path: str) -> None:
    data = read_json(path, [])
    if not isinstance(data, list):
        write_json(path, [])


def _ensure_json_dict(path: str, default: Dict[str, Any]) -> None:
    data = read_json(path, default)
    if not isinstance(data, dict):
        write_json(path, default)


def _normalize_settings() -> None:
    current = _safe_dict(read_json(SETTINGS_FILE, {}))
    normalized = {
        "default_language": str(current.get("default_language", "pt-PT")).strip() or "pt-PT",
        "author_default": str(current.get("author_default", "André Vazão")).strip() or "André Vazão",
        "updated_at": str(current.get("updated_at", now_iso())).strip() or now_iso(),
    }
    write_json(SETTINGS_FILE, normalized)


def _normalize_ips() -> None:
    ips = _safe_list(read_json(IPS_FILE, []))
    normalized = []

    for item in ips:
        if not isinstance(item, dict):
            continue

        slug = str(item.get("slug", "")).strip()
        name = str(item.get("name", "")).strip()
        if not slug or not name:
            continue

        normalized.append({
            **item,
            "slug": slug,
            "name": name,
            "default_language": str(item.get("default_language", "pt-PT")).strip() or "pt-PT",
            "output_languages": item.get("output_languages") if isinstance(item.get("output_languages"), list) and item.get("output_languages") else ["pt-PT"],
            "metadata": _safe_dict(item.get("metadata", {})),
            "palette": _safe_dict(item.get("palette", {})),
            "brand_assets": _safe_dict(item.get("brand_assets", {})),
            "main_characters": _safe_list(item.get("main_characters", [])),
            "editable_by_roles": _safe_list(item.get("editable_by_roles", [])),
            "publishable_by_roles": _safe_list(item.get("publishable_by_roles", [])),
            "allowed_editor_user_ids": _safe_list(item.get("allowed_editor_user_ids", [])),
            "allowed_editor_names": _safe_list(item.get("allowed_editor_names", [])),
        })

    write_json(IPS_FILE, normalized)


def _normalize_projects() -> None:
    projects = _safe_list(read_json(PROJECTS_FILE, []))
    normalized = []

    for item in projects:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title", "")).strip()
        if not title:
            continue

        language = str(item.get("language", "pt-PT")).strip() or "pt-PT"

        normalized.append({
            **item,
            "title": title,
            "saga_slug": str(item.get("saga_slug", "baribudos")).strip() or "baribudos",
            "saga_name": str(item.get("saga_name", "Baribudos")).strip() or "Baribudos",
            "language": language,
            "output_languages": item.get("output_languages") if isinstance(item.get("output_languages"), list) and item.get("output_languages") else [language],
            "story": _safe_dict(item.get("story", {})),
            "language_variants": _safe_dict(item.get("language_variants", {})),
            "commercial": _safe_dict(item.get("commercial", {})),
            "outputs": _safe_dict(item.get("outputs", {})),
            "factory": _safe_dict(item.get("factory", {})),
            "front_matter": _safe_dict(item.get("front_matter", {})),
            "ready_for_publish": bool(item.get("ready_for_publish", False)),
        })

    write_json(PROJECTS_FILE, normalized)


def bootstrap_system() -> Dict[str, Any]:
    ensure_storage_structure()

    _ensure_json_list(USERS_FILE)
    _ensure_json_list(PROJECTS_FILE)
    _ensure_json_list(IPS_FILE)
    _ensure_json_list(SMOKE_RESULTS_FILE)
    _ensure_json_list(PUBLICATIONS_FILE)
    _ensure_json_list(JOBS_FILE)
    _ensure_json_list(SAGAS_FILE)
    _ensure_json_list(SPONSORS_FILE)
    _ensure_json_dict(SETTINGS_FILE, {})

    _normalize_settings()
    _normalize_ips()
    _normalize_projects()

    return {
        "ok": True,
        "bootstrapped_at": now_iso(),
        "files": {
            "users": USERS_FILE,
            "projects": PROJECTS_FILE,
            "ips": IPS_FILE,
            "smoke_results": SMOKE_RESULTS_FILE,
            "publications": PUBLICATIONS_FILE,
            "settings": SETTINGS_FILE,
            "jobs": JOBS_FILE,
            "sagas": SAGAS_FILE,
            "sponsors": SPONSORS_FILE,
        },
}
