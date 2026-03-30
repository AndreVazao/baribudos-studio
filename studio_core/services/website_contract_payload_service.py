from __future__ import annotations

from typing import Any, Dict

from studio_core.services.publication_package_service import build_publication_package


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _build_short_description(description: str, fallback: str = "") -> str:
    text = _normalize_text(fallback) or _normalize_text(description)
    if len(text) <= 180:
        return text
    return f"{text[:177].rstrip()}..."


def build_website_payload_from_package(package: Dict[str, Any]) -> Dict[str, Any]:
    package = _safe_dict(package)
    website_payload = _safe_dict(package.get("website_payload"))
    commercial = _safe_dict(package.get("commercial"))
    editorial = _safe_dict(package.get("editorial"))
    outputs = _safe_dict(package.get("outputs"))
    raw_assets = _safe_dict(website_payload.get("assets"))
    seo = _safe_dict(website_payload.get("seo"))

    description = _normalize_text(website_payload.get("description"))
    subtitle = _normalize_text(commercial.get("subtitle")) or _normalize_text(website_payload.get("subtitle"))
    short_description = _build_short_description(description, commercial.get("blurb"))

    logos: list[str] = []
    primary_logo = _normalize_text(raw_assets.get("primary_logo"))
    if primary_logo:
        logos.append(primary_logo)
    for item in _safe_list(raw_assets.get("secondary_logos")):
        url = _normalize_text(item)
        if url and url not in logos:
            logos.append(url)

    downloadable_files: list[str] = []
    epub_outputs = _safe_dict(outputs.get("epub"))
    for item in epub_outputs.values():
        file_path = _normalize_text(_safe_dict(item).get("file_path"))
        if file_path:
            downloadable_files.append(file_path)

    payload = {
        "project_id": _normalize_text(website_payload.get("project_id")),
        "project_slug": _normalize_text(website_payload.get("project_slug")),
        "ip_slug": _normalize_text(website_payload.get("ip_slug")),
        "ip_name": _normalize_text(website_payload.get("ip_name")),
        "series_name": _normalize_text(website_payload.get("series_name")),
        "language": _normalize_text(website_payload.get("language")) or "pt-PT",
        "title": _normalize_text(website_payload.get("title")),
        "subtitle": subtitle,
        "description": description,
        "short_description": short_description,
        "formats": _safe_list(website_payload.get("formats")),
        "price": website_payload.get("price") if website_payload.get("price") not in {None, ""} else 0,
        "currency": _normalize_text(website_payload.get("currency")) or "EUR",
        "channel": _normalize_text(website_payload.get("channel")) or "website",
        "assets": {
            "cover": _normalize_text(raw_assets.get("cover")),
            "logos": logos,
            "gallery": _safe_list(raw_assets.get("gallery")),
            "sample_pages": _safe_list(raw_assets.get("sample_pages")),
            "audiobook_preview": raw_assets.get("audiobook_preview") or None,
            "video_trailer": raw_assets.get("video_trailer") or raw_assets.get("trailer_thumbnail") or None,
            "downloadable_files": downloadable_files,
            "studio_logo": raw_assets.get("studio_logo") or "",
            "primary_logo": raw_assets.get("primary_logo") or "",
            "secondary_logos": _safe_list(raw_assets.get("secondary_logos")),
            "hero_background": raw_assets.get("hero_background") or "",
            "ornaments": _safe_list(raw_assets.get("ornaments")),
            "badges": _safe_list(raw_assets.get("badges")),
            "promo_banners": _safe_list(raw_assets.get("promo_banners")),
            "trailer_thumbnail": raw_assets.get("trailer_thumbnail") or "",
            "character_cards": _safe_list(raw_assets.get("character_cards")),
            "background_textures": _safe_list(raw_assets.get("background_textures")),
            "social_cards": _safe_list(raw_assets.get("social_cards")),
            "campaign_visuals": _safe_list(raw_assets.get("campaign_visuals")),
        },
        "seo": {
            "title": _normalize_text(seo.get("title")) or _normalize_text(website_payload.get("title")),
            "description": _normalize_text(seo.get("description")) or description,
            "keywords": _safe_list(seo.get("keywords")),
            "canonical_url": _normalize_text(seo.get("canonical_url")),
            "og_image": _normalize_text(seo.get("og_image")),
        },
        "variant_id": _normalize_text(website_payload.get("variant_id")),
        "characters": [item for item in _safe_list(website_payload.get("characters")) if _normalize_text(item)],
        "themes": [item for item in _safe_list(website_payload.get("themes")) if _normalize_text(item)],
        "values": [item for item in _safe_list(website_payload.get("values")) if _normalize_text(item)],
        "authors": [item for item in _safe_list(website_payload.get("authors")) if _normalize_text(item)],
        "badges": [item for item in _safe_list(website_payload.get("badges")) if _normalize_text(item)],
        "video_trailer": raw_assets.get("video_trailer") or raw_assets.get("trailer_thumbnail") or None,
        "buy_links": _safe_list(website_payload.get("buy_links")),
    }

    if not payload["subtitle"]:
        payload["subtitle"] = _normalize_text(editorial.get("tagline"))

    return payload


def build_website_payload(project: Dict[str, Any]) -> Dict[str, Any]:
    package = build_publication_package(project)
    return build_website_payload_from_package(package)
