from __future__ import annotations

from typing import Any, Dict, List

from studio_core.services.branding_pack_service import build_channel_branding_pack


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def build_marketplace_visual_adaptation(
    *,
    channel: str,
    ip_slug: str | None = None,
    project_id: str | None = None,
    language: str | None = None,
) -> Dict[str, Any]:
    pack_result = build_channel_branding_pack(
        channel=channel,
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
    )

    pack = _safe_dict(pack_result.get("pack"))

    return {
        "ok": True,
        "channel": channel,
        "ip_slug": ip_slug,
        "project_id": project_id,
        "language": language,
        "adaptation": {
            "primary_visual": (
                pack.get("cover")
                or pack.get("hero_background")
                or pack.get("logo")
            ),
            "secondary_visuals": (
                _safe_list(pack.get("promo_banners"))
                or _safe_list(pack.get("gallery"))
                or _safe_list(pack.get("campaign_visuals"))
            ),
            "logo": pack.get("logo"),
            "hero_background": pack.get("hero_background"),
            "cover": pack.get("cover"),
            "gallery": _safe_list(pack.get("gallery")),
            "badges": _safe_list(pack.get("badges")),
            "promo_banners": _safe_list(pack.get("promo_banners")),
            "social_cards": _safe_list(pack.get("social_cards")),
            "campaign_visuals": _safe_list(pack.get("campaign_visuals")),
            "background_textures": _safe_list(pack.get("background_textures")),
            "trailer_thumbnail": pack.get("trailer_thumbnail"),
        },
    }


def build_amazon_visual_adaptation(
    *,
    ip_slug: str | None = None,
    project_id: str | None = None,
    language: str | None = None,
) -> Dict[str, Any]:
    return build_marketplace_visual_adaptation(
        channel="amazon",
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
    )


def build_website_visual_adaptation(
    *,
    ip_slug: str | None = None,
    project_id: str | None = None,
    language: str | None = None,
) -> Dict[str, Any]:
    return build_marketplace_visual_adaptation(
        channel="website",
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
    )


def build_social_visual_adaptation(
    *,
    ip_slug: str | None = None,
    project_id: str | None = None,
    language: str | None = None,
) -> Dict[str, Any]:
    return build_marketplace_visual_adaptation(
        channel="social",
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
  )
