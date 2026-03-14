from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from studio_core.core.config import resolve_project_path
from studio_core.services.ip_creator_service import get_ip_by_slug


def _load_json(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_public_asset(relative_path: str) -> str | None:
    relative_path = str(relative_path or "").strip()
    if not relative_path:
        return None

    if relative_path.startswith("public/"):
        path = resolve_project_path(relative_path)
        return str(path) if path.exists() else None

    path = resolve_project_path("public", relative_path.lstrip("/"))
    return str(path) if path.exists() else None


def load_ip_runtime(slug: str) -> Dict[str, Any]:
    ip = get_ip_by_slug(slug)
    if not ip:
        raise FileNotFoundError(f"IP não encontrada: {slug}")

    saga_root = resolve_project_path("studio", "sagas", slug)

    visual_canon = _load_json(saga_root / "visual-canon.json") or {}
    narrative_canon = _load_json(saga_root / "narrative-canon.json") or {}
    episode_canon = _load_json(saga_root / "episode-canon.json") or {}
    series_arc_canon = _load_json(saga_root / "series-arc-canon.json") or {}
    pedagogical_canon = _load_json(saga_root / "pedagogical-canon.json") or {}
    age_badge_canon = _load_json(saga_root / "age-badge-canon.json") or {}
    characters_master = _load_json(saga_root / "characters-master.json") or {}

    brand_assets = ip.get("brand_assets", {}) or {}
    metadata = ip.get("metadata", {}) or {}

    return {
        "ip": ip,
        "slug": ip.get("slug", slug),
        "name": ip.get("name", slug),
        "default_language": ip.get("default_language", "pt-PT"),
        "output_languages": ip.get("output_languages", ["pt-PT"]),
        "metadata": {
            "author_default": metadata.get("author_default", ""),
            "producer": metadata.get("producer", ""),
            "tagline": metadata.get("tagline", ""),
            "mission": metadata.get("mission", ""),
            "target_age": metadata.get("target_age", ""),
            "series_name": metadata.get("series_name", ""),
            "genre": metadata.get("genre", ""),
            "description": metadata.get("description", ""),
        },
        "palette": ip.get("palette", {}) or {},
        "brand_assets": {
            "studio_logo": _resolve_public_asset(brand_assets.get("studio_logo", "")),
            "series_logo": _resolve_public_asset(brand_assets.get("series_logo", "")),
            "seal_logo": _resolve_public_asset(brand_assets.get("seal_logo", "")),
        },
        "canons": {
            "visual": visual_canon,
            "narrative": narrative_canon,
            "episode": episode_canon,
            "series_arc": series_arc_canon,
            "pedagogical": pedagogical_canon,
            "age_badge": age_badge_canon,
            "characters": characters_master,
        },
        "main_characters": ip.get("main_characters", []) or [],
    }
