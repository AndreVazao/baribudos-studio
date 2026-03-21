from __future__ import annotations

from typing import Any, Dict, List

from studio_core.services.branding_resolver_service import resolve_brand_assets


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def build_branding_pack(
    *,
    context: str,
    channel: str = "",
    ip_slug: str | None = None,
    project_id: str | None = None,
    language: str | None = None,
) -> Dict[str, Any]:
    resolved = resolve_brand_assets(
        context=context,
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
        channel=channel,
    )

    assets = _safe_dict(resolved.get("assets"))

    return {
        "ok": True,
        "context": context,
        "channel": channel,
        "ip_slug": ip_slug,
        "project_id": project_id,
        "language": language,
        "strategy": resolved.get("strategy", ""),
        "pack": {
            "logo": assets.get("primary_logo") or assets.get("cover") or assets.get("studio_logo"),
            "secondary_logos": _safe_list(assets.get("secondary_logos")),
            "hero_background": assets.get("hero_background"),
            "gallery": _safe_list(assets.get("gallery")),
            "ornaments": _safe_list(assets.get("ornaments")),
            "badges": _safe_list(assets.get("badges")),
            "promo_banners": _safe_list(assets.get("promo_banners")),
            "social_cards": _safe_list(assets.get("social_cards")),
            "campaign_visuals": _safe_list(assets.get("campaign_visuals")),
            "background_textures": _safe_list(assets.get("background_textures")),
            "cover": assets.get("cover"),
            "trailer_thumbnail": assets.get("trailer_thumbnail"),
        },
    }


def build_channel_branding_pack(
    *,
    channel: str,
    ip_slug: str | None = None,
    project_id: str | None = None,
    language: str | None = None,
) -> Dict[str, Any]:
    channel = str(channel or "").strip().lower()

    if channel == "website":
        return build_branding_pack(
            context="product_page" if project_id else "homepage",
            channel=channel,
            ip_slug=ip_slug,
            project_id=project_id,
            language=language,
        )

    if channel == "amazon":
        return build_branding_pack(
            context="marketplace_amazon",
            channel=channel,
            ip_slug=ip_slug,
            project_id=project_id,
            language=language,
        )

    if channel == "social":
        return build_branding_pack(
            context="social",
            channel=channel,
            ip_slug=ip_slug,
            project_id=project_id,
            language=language,
        )

    if channel == "campaign":
        return build_branding_pack(
            context="campaign",
            channel=channel,
            ip_slug=ip_slug,
            project_id=project_id,
            language=language,
        )

    return build_branding_pack(
        context="homepage",
        channel=channel,
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
  )
