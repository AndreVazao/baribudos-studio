from __future__ import annotations

from fastapi import HTTPException, status

from studio_core.services.auth_principal import AuthenticatedPrincipal


def require_project_access(project: dict, principal: AuthenticatedPrincipal) -> None:
    """Allow administrators globally and editors only on their own projects."""
    role = str(principal.role or "").strip().lower()
    if role in {"owner", "admin"}:
        return
    if role == "editor" and str(project.get("created_by", "")).strip() == principal.user_id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Não tens permissões para aceder a este projeto.",
    )
