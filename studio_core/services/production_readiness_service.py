from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.models import now_iso
from studio_core.core.storage import get_json_item, update_json_item
from studio_core.services.publication_package_service import build_publication_package

PROJECTS_FILE = "data/projects.json"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _story_text(project: Dict[str, Any]) -> str:
    story = project.get("story")
    if isinstance(story, str):
        return _text(story)
    if isinstance(story, dict):
        return _text(story.get("raw_text"))
    return ""


def _marketing(project: Dict[str, Any]) -> Dict[str, Any]:
    commercial = _safe_dict(project.get("commercial"))
    return _safe_dict(commercial.get("website_marketing") or commercial.get("marketing"))


def _website_sync(project: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(project.get("website_sync"))


def _outputs(project: Dict[str, Any]) -> Dict[str, Any]:
    return _safe_dict(project.get("outputs"))


def _label_for_ratio(ratio: float) -> Dict[str, str]:
    if ratio >= 1:
        return {"label": "Operationally ready", "color": "#166534", "bg": "rgba(34,197,94,0.12)"}
    if ratio >= 0.75:
        return {"label": "Almost ready", "color": "#1d4ed8", "bg": "rgba(59,130,246,0.12)"}
    if ratio >= 0.5:
        return {"label": "Needs key production closures", "color": "#92400e", "bg": "rgba(245,158,11,0.14)"}
    return {"label": "Not ready", "color": "#991b1b", "bg": "rgba(239,68,68,0.10)"}


def _build_section_summary(name: str, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
    completed = len([item for item in checks if item.get("ok")])
    total = len(checks)
    ratio = (completed / total) if total else 0
    meta = _label_for_ratio(ratio)
    return {
        "name": name,
        "checks": checks,
        "completed": completed,
        "total": total,
        "ratio": ratio,
        "label": meta["label"],
        "color": meta["color"],
        "bg": meta["bg"],
    }


def build_production_readiness(project: Dict[str, Any]) -> Dict[str, Any]:
    marketing = _marketing(project)
    website_sync = _website_sync(project)
    outputs = _outputs(project)
    story_text = _story_text(project)
    publication_package = _safe_dict(project.get("publication_package"))
    frozen_at = _text(project.get("publication_package_frozen_at"))

    production_checks = [
        {"key": "title", "label": "Project title", "ok": bool(_text(project.get("title")))},
        {"key": "language", "label": "Primary language", "ok": bool(_text(project.get("language")))},
        {"key": "story", "label": "Story raw text", "ok": bool(story_text)},
        {"key": "cover", "label": "Cover image", "ok": bool(_text(project.get("cover_image")) or _text(project.get("illustration_path")))},
        {"key": "outputs", "label": "Any production output", "ok": bool(outputs)},
    ]

    commercial_checks = [
        {"key": "headline", "label": "Website headline", "ok": bool(_text(marketing.get("teaser_headline")))},
        {"key": "subtitle", "label": "Website subtitle", "ok": bool(_text(marketing.get("teaser_subtitle")))},
        {"key": "cta", "label": "Website CTA", "ok": bool(_text(marketing.get("teaser_cta_label")))},
        {"key": "cover", "label": "Website cover", "ok": bool(_text(marketing.get("teaser_cover_url")) or _text(project.get("cover_image")))},
        {"key": "gallery", "label": "Website gallery", "ok": len(_safe_list(marketing.get("teaser_gallery"))) > 0},
        {"key": "public-state", "label": "Public state prepared", "ok": _text(marketing.get("public_state")) in {"teaser_ready", "prelaunch_public", "launch_ready", "published"}},
    ]

    package_checks = [
        {"key": "package", "label": "Publication package exists", "ok": bool(publication_package)},
        {"key": "frozen-at", "label": "Publication package frozen", "ok": bool(frozen_at)},
        {"key": "ready-for-publish", "label": "ready_for_publish flag", "ok": bool(project.get("ready_for_publish"))},
    ]

    website_checks = [
        {"key": "sync-id", "label": "Website publication id known", "ok": bool(_text(website_sync.get("publication_id")))},
        {"key": "sync-published", "label": "Website published or revalidated", "ok": bool(_text(website_sync.get("published_at")) or _text(website_sync.get("last_revalidate_at")))},
    ]

    ebook_checks = [
        {"key": "package-frozen", "label": "Package frozen for ebook", "ok": bool(frozen_at)},
        {"key": "commercial-copy", "label": "Commercial copy exists", "ok": bool(_text(marketing.get("teaser_subtitle")) or _text(marketing.get("teaser_excerpt")))},
        {"key": "cover-ready", "label": "Cover ready", "ok": bool(_text(marketing.get("teaser_cover_url")) or _text(project.get("cover_image")))},
    ]

    audiobook_checks = [
        {"key": "story", "label": "Story text exists", "ok": bool(story_text)},
        {"key": "commercial-copy", "label": "Commercial copy exists", "ok": bool(_text(marketing.get("teaser_excerpt")) or _text(marketing.get("teaser_subtitle")))},
        {"key": "cover-ready", "label": "Cover ready", "ok": bool(_text(marketing.get("teaser_cover_url")) or _text(project.get("cover_image")))},
    ]

    sections = {
        "production": _build_section_summary("production", production_checks),
        "commercial": _build_section_summary("commercial", commercial_checks),
        "publication": _build_section_summary("publication", package_checks),
        "website": _build_section_summary("website", website_checks),
        "ebook": _build_section_summary("ebook", ebook_checks),
        "audiobook": _build_section_summary("audiobook", audiobook_checks),
    }

    total_checks = sum(section["total"] for section in sections.values())
    completed_checks = sum(section["completed"] for section in sections.values())
    ratio = (completed_checks / total_checks) if total_checks else 0
    meta = _label_for_ratio(ratio)

    package_readiness = {}
    try:
        package_snapshot = build_publication_package(project)
        package_readiness = _safe_dict(_safe_dict(package_snapshot.get("checks")).get("readiness"))
    except Exception as exc:
        package_readiness = {
            "ready": False,
            "label": "Package build failed",
            "error": str(exc),
        }

    return {
        "project_id": _text(project.get("id")),
        "project_title": _text(project.get("title")),
        "ready_for_publish": bool(project.get("ready_for_publish")),
        "publication_package_frozen_at": frozen_at,
        "package_readiness": package_readiness,
        "sections": sections,
        "completed": completed_checks,
        "total": total_checks,
        "ratio": ratio,
        "label": meta["label"],
        "color": meta["color"],
        "bg": meta["bg"],
        "generated_at": now_iso(),
    }


def get_production_readiness(project_id: str) -> Dict[str, Any]:
    project = get_json_item(PROJECTS_FILE, project_id)
    if not project:
        raise ValueError("project_not_found")
    return build_production_readiness(project)


def sync_ready_for_publish_with_readiness(project_id: str) -> Dict[str, Any]:
    project = get_json_item(PROJECTS_FILE, project_id)
    if not project:
        raise ValueError("project_not_found")

    readiness = build_production_readiness(project)
    package_ready = bool(_safe_dict(readiness.get("package_readiness")).get("ready", False))
    operational_ready = readiness.get("ratio", 0) >= 0.75
    final_ready = bool(package_ready and operational_ready)

    updated = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "ready_for_publish": final_ready,
            "production_readiness": readiness,
            "production_readiness_synced_at": now_iso(),
            "updated_at": now_iso(),
        },
    )

    return {
        "ok": True,
        "project_id": project_id,
        "ready_for_publish": bool(updated.get("ready_for_publish")),
        "production_readiness": readiness,
    }
