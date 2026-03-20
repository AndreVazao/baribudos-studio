from __future__ import annotations

from typing import Any, Dict, List, Optional

from studio_core.services.asset_registry_service import (
    get_assets,
    get_primary_asset,
)


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _first_or_none(items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return items[0] if items else None


def _published_assets(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    return get_assets({
        **filters,
        "status": "published",
    })


def _published_primary(filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return get_primary_asset({
        **filters,
        "status": "published",
    })


def _resolve_global_assets() -> Dict[str, Any]:
    primary_logo = _published_primary({
        "asset_type": "studio_logo",
    })

    secondary_logos = _published_assets({
        "asset_type": "studio_logo",
    })

    hero_background = _published_primary({
        "asset_type": "hero_background",
        "context": "homepage",
    })

    decorative_assets = _published_assets({
        "asset_type": "ornament",
        "context": "homepage",
    })

    campaign_assets = _published_assets({
        "asset_type": "campaign_visual",
        "context": "homepage",
    })

    return {
        "scope": "global",
        "primary_logo": primary_logo,
        "secondary_logos": secondary_logos,
        "hero_background": hero_background,
        "decorative_assets": decorative_assets,
        "campaign_assets": campaign_assets,
    }


def _resolve_ip_assets(ip_slug: str) -> Dict[str, Any]:
    primary_logo = _published_primary({
        "asset_type": "ip_logo",
        "ip_slug": ip_slug,
    })

    secondary_logos = _published_assets({
        "asset_type": "ip_logo",
        "ip_slug": ip_slug,
    })

    hero_background = _published_primary({
        "asset_type": "hero_background",
        "ip_slug": ip_slug,
    })

    decorative_assets = _published_assets({
        "asset_type": "ornament",
        "ip_slug": ip_slug,
    })

    badges = _published_assets({
        "asset_type": "badge",
        "ip_slug": ip_slug,
    })

    campaign_assets = _published_assets({
        "asset_type": "campaign_visual",
        "ip_slug": ip_slug,
    })

    background_textures = _published_assets({
        "asset_type": "background_texture",
        "ip_slug": ip_slug,
    })

    return {
        "scope": "ip",
        "ip_slug": ip_slug,
        "primary_logo": primary_logo,
        "secondary_logos": secondary_logos,
        "hero_background": hero_background,
        "decorative_assets": decorative_assets,
        "badges": badges,
        "campaign_assets": campaign_assets,
        "background_textures": background_textures,
    }


def _resolve_product_assets(project_id: str, ip_slug: str | None = None) -> Dict[str, Any]:
    cover = _published_primary({
        "project_id": project_id,
        "asset_type": "cover",
    })

    hero_background = _published_primary({
        "project_id": project_id,
        "asset_type": "hero_background",
    })

    gallery = _published_assets({
        "project_id": project_id,
        "asset_type": "gallery_image",
    })

    promo_banners = _published_assets({
        "project_id": project_id,
        "asset_type": "promo_banner",
    })

    trailer_thumbnail = _published_primary({
        "project_id": project_id,
        "asset_type": "trailer_thumbnail",
    })

    character_cards = _published_assets({
        "project_id": project_id,
        "asset_type": "character_card",
    })

    ip_assets = _resolve_ip_assets(ip_slug) if _safe_str(ip_slug) else {}

    return {
        "scope": "product",
        "project_id": project_id,
        "cover": cover,
        "hero_background": hero_background,
        "gallery": gallery,
        "promo_banners": promo_banners,
        "trailer_thumbnail": trailer_thumbnail,
        "character_cards": character_cards,
        "ip_assets": ip_assets,
    }


def resolve_brand_assets(
    context: str,
    ip_slug: str | None = None,
    project_id: str | None = None,
) -> Dict[str, Any]:
    """
    Hierarquia editorial:
    1. Página institucional -> studio_logo
    2. Página IP -> ip_logo
    3. Página produto -> cover + ip assets
    """

    normalized_context = _safe_str(context).lower()
    normalized_ip_slug = _safe_str(ip_slug)
    normalized_project_id = _safe_str(project_id)

    if normalized_context in {"global", "homepage", "global_header", "global_footer"}:
        return {
            "ok": True,
            "context": normalized_context,
            "strategy": "studio_logo_priority",
            "assets": _resolve_global_assets(),
        }

    if normalized_context in {"ip", "ip_page", "library", "campaign", "marketing_landing"}:
        return {
            "ok": True,
            "context": normalized_context,
            "strategy": "ip_logo_priority",
            "assets": _resolve_ip_assets(normalized_ip_slug),
        }

    if normalized_context in {"product", "product_page", "marketplace_website", "marketplace_amazon"}:
        return {
            "ok": True,
            "context": normalized_context,
            "strategy": "cover_plus_ip_assets",
            "assets": _resolve_product_assets(normalized_project_id, normalized_ip_slug),
        }

    # fallback genérico por contexto
    primary_logo = None
    if normalized_ip_slug:
        primary_logo = _published_primary({
            "asset_type": "ip_logo",
            "ip_slug": normalized_ip_slug,
            "context": normalized_context,
        })

    if not primary_logo:
        primary_logo = _published_primary({
            "asset_type": "studio_logo",
            "context": normalized_context,
        })

    hero_background = _published_primary({
        "asset_type": "hero_background",
        "context": normalized_context,
        "ip_slug": normalized_ip_slug or None,
        "project_id": normalized_project_id or None,
    })

    decorative_assets = _published_assets({
        "asset_type": "ornament",
        "context": normalized_context,
        "ip_slug": normalized_ip_slug or None,
    })

    campaign_assets = _published_assets({
        "asset_type": "campaign_visual",
        "context": normalized_context,
        "ip_slug": normalized_ip_slug or None,
    })

    return {
        "ok": True,
        "context": normalized_context,
        "strategy": "context_fallback_resolution",
        "assets": {
            "primary_logo": primary_logo,
            "hero_background": hero_background,
            "decorative_assets": decorative_assets,
            "campaign_assets": campaign_assets,
        },
    }


# Compatibilidade com o que já tinhas
def resolveBrandAssets(context, ip_slug=None, project_id=None):
    return resolve_brand_assets(
        context=context,
        ip_slug=ip_slug,
        project_id=project_id,
    )
