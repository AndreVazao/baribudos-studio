from __future__ import annotations

from typing import Any, Dict, List, Optional

from studio_core.services.asset_registry_service import get_assets, get_primary_asset
from studio_core.services.cdn_service import resolve_cdn_url


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _asset_url(asset: Dict[str, Any] | None) -> str | None:
    if not asset:
        return None
    return resolve_cdn_url(asset.get("storage_path", ""), asset.get("version"))


def _asset_urls(items: List[Dict[str, Any]]) -> List[str]:
    return [
        resolve_cdn_url(item.get("storage_path", ""), item.get("version"))
        for item in items
        if item.get("storage_path")
    ]


def _published_filters(
    asset_type: str,
    *,
    context: str | None = None,
    ip_slug: str | None = None,
    project_id: str | None = None,
    language: str | None = None,
    is_primary: bool | None = None,
) -> Dict[str, Any]:
    return {
        "asset_type": asset_type,
        "context": context,
        "ip_slug": ip_slug,
        "project_id": project_id,
        "language": language,
        "is_primary": is_primary,
        "status": "published",
    }


def _get_primary(
    asset_type: str,
    *,
    context: str | None = None,
    ip_slug: str | None = None,
    project_id: str | None = None,
    language: str | None = None,
) -> Dict[str, Any] | None:
    return get_primary_asset(_published_filters(
        asset_type,
        context=context,
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
        is_primary=True,
    ))


def _get_many(
    asset_type: str,
    *,
    context: str | None = None,
    ip_slug: str | None = None,
    project_id: str | None = None,
    language: str | None = None,
) -> List[Dict[str, Any]]:
    return get_assets(_published_filters(
        asset_type,
        context=context,
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
    ))


def _resolve_global_branding(context: str, language: str | None = None) -> Dict[str, Any]:
    primary_logo = (
        _get_primary("studio_logo", context=context, language=language)
        or _get_primary("studio_logo", language=language)
        or _get_primary("studio_logo")
    )

    secondary_logos = (
        _get_many("studio_logo", context=context, language=language)
        or _get_many("studio_logo", language=language)
        or _get_many("studio_logo")
    )

    hero_background = (
        _get_primary("hero_background", context=context, language=language)
        or _get_primary("hero_background", context="homepage", language=language)
        or _get_primary("hero_background", context="homepage")
    )

    ornaments = (
        _get_many("ornament", context=context, language=language)
        or _get_many("ornament", context="homepage", language=language)
        or _get_many("ornament", context="homepage")
    )

    badges = (
        _get_many("badge", context=context, language=language)
        or _get_many("badge", language=language)
        or _get_many("badge")
    )

    campaign_visuals = (
        _get_many("campaign_visual", context=context, language=language)
        or _get_many("campaign_visual", language=language)
        or _get_many("campaign_visual")
    )

    return {
        "scope": "global",
        "primary_logo": _asset_url(primary_logo),
        "secondary_logos": _asset_urls(secondary_logos),
        "hero_background": _asset_url(hero_background),
        "ornaments": _asset_urls(ornaments),
        "badges": _asset_urls(badges),
        "campaign_visuals": _asset_urls(campaign_visuals),
    }


def _resolve_ip_branding(
    ip_slug: str,
    context: str,
    language: str | None = None,
) -> Dict[str, Any]:
    primary_logo = (
        _get_primary("ip_logo", ip_slug=ip_slug, context=context, language=language)
        or _get_primary("ip_logo", ip_slug=ip_slug, language=language)
        or _get_primary("ip_logo", ip_slug=ip_slug)
    )

    secondary_logos = (
        _get_many("ip_logo", ip_slug=ip_slug, context=context, language=language)
        or _get_many("ip_logo", ip_slug=ip_slug, language=language)
        or _get_many("ip_logo", ip_slug=ip_slug)
    )

    hero_background = (
        _get_primary("hero_background", ip_slug=ip_slug, context=context, language=language)
        or _get_primary("hero_background", ip_slug=ip_slug, language=language)
        or _get_primary("hero_background", ip_slug=ip_slug)
    )

    gallery = (
        _get_many("gallery_image", ip_slug=ip_slug, context=context, language=language)
        or _get_many("gallery_image", ip_slug=ip_slug, language=language)
        or _get_many("gallery_image", ip_slug=ip_slug)
    )

    ornaments = (
        _get_many("ornament", ip_slug=ip_slug, context=context, language=language)
        or _get_many("ornament", ip_slug=ip_slug, language=language)
        or _get_many("ornament", ip_slug=ip_slug)
    )

    badges = (
        _get_many("badge", ip_slug=ip_slug, context=context, language=language)
        or _get_many("badge", ip_slug=ip_slug, language=language)
        or _get_many("badge", ip_slug=ip_slug)
    )

    campaign_visuals = (
        _get_many("campaign_visual", ip_slug=ip_slug, context=context, language=language)
        or _get_many("campaign_visual", ip_slug=ip_slug, language=language)
        or _get_many("campaign_visual", ip_slug=ip_slug)
    )

    background_textures = (
        _get_many("background_texture", ip_slug=ip_slug, context=context, language=language)
        or _get_many("background_texture", ip_slug=ip_slug, language=language)
        or _get_many("background_texture", ip_slug=ip_slug)
    )

    social_cards = (
        _get_many("social_card", ip_slug=ip_slug, context=context, language=language)
        or _get_many("social_card", ip_slug=ip_slug, language=language)
        or _get_many("social_card", ip_slug=ip_slug)
    )

    return {
        "scope": "ip",
        "ip_slug": ip_slug,
        "primary_logo": _asset_url(primary_logo),
        "secondary_logos": _asset_urls(secondary_logos),
        "hero_background": _asset_url(hero_background),
        "gallery": _asset_urls(gallery),
        "ornaments": _asset_urls(ornaments),
        "badges": _asset_urls(badges),
        "campaign_visuals": _asset_urls(campaign_visuals),
        "background_textures": _asset_urls(background_textures),
        "social_cards": _asset_urls(social_cards),
    }


def _resolve_product_branding(
    project_id: str,
    ip_slug: str | None,
    context: str,
    language: str | None = None,
) -> Dict[str, Any]:
    cover = (
        _get_primary("cover", project_id=project_id, context=context, language=language)
        or _get_primary("cover", project_id=project_id, language=language)
        or _get_primary("cover", project_id=project_id)
    )

    hero_background = (
        _get_primary("hero_background", project_id=project_id, context=context, language=language)
        or _get_primary("hero_background", project_id=project_id, language=language)
        or _get_primary("hero_background", project_id=project_id)
    )

    gallery = (
        _get_many("gallery_image", project_id=project_id, context=context, language=language)
        or _get_many("gallery_image", project_id=project_id, language=language)
        or _get_many("gallery_image", project_id=project_id)
    )

    trailer_thumbnail = (
        _get_primary("trailer_thumbnail", project_id=project_id, context=context, language=language)
        or _get_primary("trailer_thumbnail", project_id=project_id, language=language)
        or _get_primary("trailer_thumbnail", project_id=project_id)
    )

    promo_banners = (
        _get_many("promo_banner", project_id=project_id, context=context, language=language)
        or _get_many("promo_banner", project_id=project_id, language=language)
        or _get_many("promo_banner", project_id=project_id)
    )

    social_cards = (
        _get_many("social_card", project_id=project_id, context=context, language=language)
        or _get_many("social_card", project_id=project_id, language=language)
        or _get_many("social_card", project_id=project_id)
    )

    ip_assets = _resolve_ip_branding(ip_slug, context, language) if _safe_str(ip_slug) else None

    return {
        "scope": "product",
        "project_id": project_id,
        "cover": _asset_url(cover),
        "hero_background": _asset_url(hero_background),
        "gallery": _asset_urls(gallery),
        "trailer_thumbnail": _asset_url(trailer_thumbnail),
        "promo_banners": _asset_urls(promo_banners),
        "social_cards": _asset_urls(social_cards),
        "ip_assets": ip_assets,
    }


def resolve_brand_assets(
    context: str,
    ip_slug: str | None = None,
    project_id: str | None = None,
    language: str | None = None,
    channel: str | None = None,
) -> Dict[str, Any]:
    normalized_context = _safe_str(context).lower()
    normalized_ip_slug = _safe_str(ip_slug)
    normalized_project_id = _safe_str(project_id)
    normalized_language = _safe_str(language) or None
    normalized_channel = _safe_str(channel).lower()

    institutional_contexts = {
        "global_header",
        "global_footer",
        "homepage",
        "checkout",
        "admin",
        "email",
    }

    ip_contexts = {
        "ip_page",
        "library",
        "campaign",
        "marketing_landing",
        "social",
    }

    product_contexts = {
        "product_page",
        "marketplace_amazon",
        "marketplace_website",
    }

    if normalized_context in institutional_contexts:
        return {
            "ok": True,
            "context": normalized_context,
            "channel": normalized_channel,
            "strategy": "studio_logo_priority",
            "assets": _resolve_global_branding(
                context=normalized_context,
                language=normalized_language,
            ),
        }

    if normalized_context in ip_contexts and normalized_ip_slug:
        return {
            "ok": True,
            "context": normalized_context,
            "channel": normalized_channel,
            "strategy": "ip_logo_priority",
            "assets": _resolve_ip_branding(
                ip_slug=normalized_ip_slug,
                context=normalized_context,
                language=normalized_language,
            ),
        }

    if normalized_context in product_contexts and normalized_project_id:
        return {
            "ok": True,
            "context": normalized_context,
            "channel": normalized_channel,
            "strategy": "cover_plus_ip_assets",
            "assets": _resolve_product_branding(
                project_id=normalized_project_id,
                ip_slug=normalized_ip_slug or None,
                context=normalized_context,
                language=normalized_language,
            ),
        }

    # fallback inteligente
    if normalized_project_id:
        return {
            "ok": True,
            "context": normalized_context,
            "channel": normalized_channel,
            "strategy": "fallback_product_resolution",
            "assets": _resolve_product_branding(
                project_id=normalized_project_id,
                ip_slug=normalized_ip_slug or None,
                context=normalized_context or "product_page",
                language=normalized_language,
            ),
        }

    if normalized_ip_slug:
        return {
            "ok": True,
            "context": normalized_context,
            "channel": normalized_channel,
            "strategy": "fallback_ip_resolution",
            "assets": _resolve_ip_branding(
                ip_slug=normalized_ip_slug,
                context=normalized_context or "ip_page",
                language=normalized_language,
            ),
        }

    return {
        "ok": True,
        "context": normalized_context,
        "channel": normalized_channel,
        "strategy": "fallback_global_resolution",
        "assets": _resolve_global_branding(
            context=normalized_context or "homepage",
            language=normalized_language,
        ),
    }


# compatibilidade com o que já tinhas
def resolveBrandAssets(context, ip_slug=None, project_id=None):
    result = resolve_brand_assets(
        context=context,
        ip_slug=ip_slug,
        project_id=project_id,
    )
    return result.get("assets", {})
