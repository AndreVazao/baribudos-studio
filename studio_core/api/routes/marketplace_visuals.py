from __future__ import annotations

from fastapi import APIRouter, Query

from studio_core.services.marketplace_visual_adaptation_service import (
    build_amazon_visual_adaptation,
    build_marketplace_visual_adaptation,
    build_social_visual_adaptation,
    build_website_visual_adaptation,
)

router = APIRouter(prefix="/marketplace-visuals", tags=["marketplace-visuals"])


@router.get("/channel")
def marketplace_visuals_by_channel(
    channel: str = Query(...),
    ip_slug: str | None = Query(default=None),
    project_id: str | None = Query(default=None),
    language: str | None = Query(default=None),
) -> dict:
    return build_marketplace_visual_adaptation(
        channel=channel,
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
    )


@router.get("/amazon")
def amazon_visuals(
    ip_slug: str | None = Query(default=None),
    project_id: str | None = Query(default=None),
    language: str | None = Query(default=None),
) -> dict:
    return build_amazon_visual_adaptation(
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
    )


@router.get("/website")
def website_visuals(
    ip_slug: str | None = Query(default=None),
    project_id: str | None = Query(default=None),
    language: str | None = Query(default=None),
) -> dict:
    return build_website_visual_adaptation(
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
    )


@router.get("/social")
def social_visuals(
    ip_slug: str | None = Query(default=None),
    project_id: str | None = Query(default=None),
    language: str | None = Query(default=None),
) -> dict:
    return build_social_visual_adaptation(
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
)
