from __future__ import annotations

from typing import Any, Dict, List

from studio_core.services.publication_package_builder import build_publication_package


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _slugify(value: str) -> str:
    return str(value or "").lower().replace(" ", "-").strip()


def build_store_payload(project: Dict[str, Any]) -> Dict[str, Any]:
    pkg = build_publication_package(project)

    project_meta = _safe_dict(pkg.get("project"))
    editorial = _safe_dict(pkg.get("editorial"))
    commercial = _safe_dict(pkg.get("commercial"))
    assets = _safe_dict(pkg.get("assets", {}).get("public"))

    title = project_meta.get("title", "")
    language = project_meta.get("language", "")
    ip_slug = project_meta.get("saga_slug", "")
    ip_name = project_meta.get("saga_name", "")
    series_name = editorial.get("series_name", "")

    slug = _slugify(f"{ip_slug}-{title}-{language}")

    return {
        "project_id": project_meta.get("id"),
        "project_slug": slug,
        "ip_slug": ip_slug,
        "ip_name": ip_name,
        "series_name": series_name,
        "language": language,
        "title": title,
        "description": editorial.get("description", ""),
        "formats": _build_formats(pkg),
        "price": commercial.get("price"),
        "currency": commercial.get("currency"),
        "seo": _build_seo(project_meta, editorial, commercial),
        "assets": assets,
        "variant_id": f"{slug}-{language}",
        "channel": _build_channel(commercial),
        "characters": [],
        "themes": [],
        "values": [],
        "authors": [editorial.get("author_default")],
        "badges": _safe_list(assets.get("badges")),
        "video_trailer": assets.get("trailer_thumbnail"),
        "buy_links": _safe_list(commercial.get("marketplaces")),
    }


def _build_formats(pkg: Dict[str, Any]) -> List[str]:
    outputs = _safe_dict(pkg.get("outputs"))

    formats = []

    if outputs.get("epub"):
        formats.append("ebook")

    if outputs.get("audiobook"):
        formats.append("audiobook")

    if outputs.get("video"):
        formats.append("video")

    return formats


def _build_channel(commercial: Dict[str, Any]) -> str:
    channels = _safe_list(commercial.get("channels"))

    if "amazon" in channels:
        return "amazon"

    if "website" in channels:
        return "website"

    return "direct"


def _build_seo(project_meta, editorial, commercial):
    return {
        "keywords": _safe_list(commercial.get("keywords")),
        "subtitle": commercial.get("subtitle"),
        "tagline": editorial.get("tagline"),
        "mission": editorial.get("mission"),
        "target_age": editorial.get("target_age"),
}
