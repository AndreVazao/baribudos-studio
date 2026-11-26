from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.ip_route_auth import assert_ip_read_access
from studio_core.services.project_route_auth import assert_project_access
from studio_core.services.branding_pack_service import build_branding_pack, build_channel_branding_pack

router = APIRouter(prefix="/branding-pack", tags=["branding-pack"])


def _authorize_pack(project_id: str | None, ip_slug: str | None, principal: AuthenticatedPrincipal) -> None:
    if project_id:
        assert_project_access(project_id, principal)
    if ip_slug:
        assert_ip_read_access(ip_slug, principal)


@router.get("/context")
def branding_pack_by_context(
    context: str = Query(...),
    channel: str = Query(default=""),
    ip_slug: str | None = Query(default=None),
    project_id: str | None = Query(default=None),
    language: str | None = Query(default=None),
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    _authorize_pack(project_id, ip_slug, principal)
    return build_branding_pack(context=context, channel=channel, ip_slug=ip_slug, project_id=project_id, language=language)


@router.get("/channel")
def branding_pack_by_channel(
    channel: str = Query(...),
    ip_slug: str | None = Query(default=None),
    project_id: str | None = Query(default=None),
    language: str | None = Query(default=None),
    principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin", "editor", "creator")),
) -> dict:
    _authorize_pack(project_id, ip_slug, principal)
    return build_channel_branding_pack(channel=channel, ip_slug=ip_slug, project_id=project_id, language=language)
