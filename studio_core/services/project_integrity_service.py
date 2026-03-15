from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from studio_core.services.publication_package_service import build_publication_package


def _exists_file(value: str) -> bool:
    path = str(value or "").strip()
    if not path:
        return False
    try:
        return Path(path).exists() and Path(path).is_file()
    except Exception:
        return False


def _normalize_output_map(output_map: Any) -> Dict[str, Any]:
    if isinstance(output_map, dict):
        return output_map
    return {}


def audit_project_integrity(project: Dict[str, Any]) -> Dict[str, Any]:
    outputs = project.get("outputs", {}) or {}
    covers = outputs.get("covers") or {}
    epub = _normalize_output_map(outputs.get("epub"))
    audiobook = _normalize_output_map(outputs.get("audiobook"))
    video = _normalize_output_map(outputs.get("video"))

    file_checks: List[Dict[str, Any]] = []

    def add_check(group: str, label: str, file_path: str) -> None:
        file_checks.append({
            "group": group,
            "label": label,
            "file_path": file_path,
            "exists": _exists_file(file_path),
        })

    add_check("project", "cover_image", project.get("cover_image", ""))
    add_check("project", "illustration_path", project.get("illustration_path", ""))
    add_check("covers", "cover_file", covers.get("file_path", ""))
    add_check("covers", "badge_file", covers.get("badge_file_path", ""))

    for lang, item in epub.items():
        add_check("epub", f"epub_{lang}", (item or {}).get("file_path", ""))

    for lang, item in audiobook.items():
        add_check("audiobook", f"audiobook_{lang}", (item or {}).get("file_path", ""))

    for lang, item in video.items():
        add_check("video", f"video_{lang}", (item or {}).get("file_path", ""))

    missing_files = [item for item in file_checks if item["file_path"] and not item["exists"]]

    publication_package = build_publication_package(project)
    readiness = ((publication_package.get("checks") or {}).get("readiness", {})) or {}
    runtime = publication_package.get("runtime", {}) or {}

    return {
        "project_id": project.get("id"),
        "title": project.get("title"),
        "runtime_slug": runtime.get("slug", ""),
        "runtime_name": runtime.get("name", ""),
        "runtime_validation": runtime.get("validation", {}),
        "file_checks": file_checks,
        "missing_files": missing_files,
        "missing_files_count": len(missing_files),
        "ready_for_publish_flag": bool(project.get("ready_for_publish", False)),
        "readiness_status": readiness.get("status", "red"),
        "readiness_ready": bool(readiness.get("ready", False)),
        "integrity_ok": len(missing_files) == 0,
    }


def repair_project_structure(project: Dict[str, Any]) -> Dict[str, Any]:
    outputs = project.get("outputs", {})
    if not isinstance(outputs, dict):
        outputs = {}

    epub = outputs.get("epub", {})
    audiobook = outputs.get("audiobook", {})
    video = outputs.get("video", {})

    if not isinstance(epub, dict):
        epub = {}
    if not isinstance(audiobook, dict):
        audiobook = {}
    if not isinstance(video, dict):
        video = {}

    commercial = project.get("commercial", {})
    if not isinstance(commercial, dict):
        commercial = {}

    story = project.get("story", {})
    if not isinstance(story, dict):
        story = {}

    repaired = {
        **project,
        "language": str(project.get("language", "pt-PT")).strip() or "pt-PT",
        "output_languages": project.get("output_languages") if isinstance(project.get("output_languages"), list) and project.get("output_languages") else [str(project.get("language", "pt-PT")).strip() or "pt-PT"],
        "cover_image": str(project.get("cover_image", "")).strip(),
        "illustration_path": str(project.get("illustration_path", "")).strip(),
        "ready_for_publish": bool(project.get("ready_for_publish", False)),
        "commercial": {
            "internal_code": str(commercial.get("internal_code", "")).strip(),
            "isbn": str(commercial.get("isbn", "")).strip(),
            "asin": str(commercial.get("asin", "")).strip(),
            "price": str(commercial.get("price", "")).strip(),
            "currency": str(commercial.get("currency", "EUR")).strip() or "EUR",
            "collection_seal": str(commercial.get("collection_seal", "")).strip(),
            "marketplaces": commercial.get("marketplaces") if isinstance(commercial.get("marketplaces"), list) else [],
            "commercial_status": str(commercial.get("commercial_status", "draft")).strip() or "draft",
            "channels": commercial.get("channels") if isinstance(commercial.get("channels"), list) else [],
            "keywords": commercial.get("keywords") if isinstance(commercial.get("keywords"), list) else [],
            "subtitle": str(commercial.get("subtitle", "")).strip(),
            "blurb": str(commercial.get("blurb", "")).strip(),
        },
        "story": {
            "title": str(story.get("title", project.get("title", ""))).strip(),
            "language": str(story.get("language", project.get("language", "pt-PT"))).strip() or "pt-PT",
            "pages": story.get("pages") if isinstance(story.get("pages"), list) else [],
            "raw_text": str(story.get("raw_text", "")).strip(),
        },
        "outputs": {
            **outputs,
            "epub": epub,
            "audiobook": audiobook,
            "video": video,
        },
    }

    return repaired
