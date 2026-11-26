from __future__ import annotations

from fastapi import Depends, HTTPException, status

from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.ip_creator_service import get_ip_by_slug

_IP_ROLES = ("owner", "admin", "editor", "creator")


def _resolve_ip(slug: str) -> dict:
    item = get_ip_by_slug(slug)
    if not isinstance(item, dict):
        raise HTTPException(status_code=404, detail="IP não encontrada.")
    return item


def _can_view(item: dict, principal: AuthenticatedPrincipal) -> bool:
    if principal.role.lower() in {"owner", "admin"}:
        return True
    if not bool(item.get("visible_to_owner_only", False)):
        return True
    allowed = {str(value).strip() for value in item.get("allowed_editor_user_ids", []) if str(value).strip()}
    return principal.user_id == str(item.get("owner_id", "")).strip() or principal.user_id in allowed


def _can_edit(item: dict, principal: AuthenticatedPrincipal) -> bool:
    if principal.role.lower() in {"owner", "admin"}:
        return True
    if not _can_view(item, principal):
        return False
    if principal.user_id == str(item.get("owner_id", "")).strip():
        return True
    allowed = {str(value).strip() for value in item.get("allowed_editor_user_ids", []) if str(value).strip()}
    if principal.user_id in allowed:
        return True
    editable_roles = {str(value).strip().lower() for value in item.get("editable_by_roles", [])}
    return not bool(item.get("exclusive", False)) and principal.role.lower() in editable_roles


def assert_ip_read_access(slug: str, principal: AuthenticatedPrincipal) -> AuthenticatedPrincipal:
    item = _resolve_ip(slug)
    if not _can_view(item, principal):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso a esta IP.")
    return principal


def assert_ip_edit_access(slug: str, principal: AuthenticatedPrincipal) -> AuthenticatedPrincipal:
    item = _resolve_ip(slug)
    if not _can_edit(item, principal):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para editar esta IP.")
    return principal


def require_ip_read_access(
    slug: str,
    principal: AuthenticatedPrincipal = Depends(require_roles(*_IP_ROLES)),
) -> AuthenticatedPrincipal:
    return assert_ip_read_access(slug, principal)


def require_ip_edit_access(
    slug: str,
    principal: AuthenticatedPrincipal = Depends(require_roles(*_IP_ROLES)),
) -> AuthenticatedPrincipal:
    return assert_ip_edit_access(slug, principal)
