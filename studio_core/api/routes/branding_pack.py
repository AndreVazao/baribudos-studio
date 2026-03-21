from __future__ import annotations

from fastapi import APIRouter, Query

from studio_core.services.branding_pack_service import (
    build_branding_pack,
    build_channel_branding_pack,
)

router = APIRouter(prefix="/branding-pack", tags=["branding-pack"])


@router.get("/context")
def branding_pack_by_context(
    context: str = Query(...),
    channel: str = Query(default=""),
    ip_slug: str | None = Query(default=None),
    project_id: str | None = Query(default=None),
    language: str | None = Query(default=None),
) -> dict:
    return build_branding_pack(
        context=context,
        channel=channel,
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
    )


@router.get("/channel")
def branding_pack_by_channel(
    channel: str = Query(...),
    ip_slug: str | None = Query(default=None),
    project_id: str | None = Query(default=None),
    language: str | None = Query(default=None),
) -> dict:
    return build_channel_branding_pack(
        channel=channel,
        ip_slug=ip_slug,
        project_id=project_id,
        language=language,
                                  )
