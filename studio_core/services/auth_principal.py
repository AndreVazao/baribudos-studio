"""Resolve an authenticated principal exclusively from a server-side session.

The caller's user ID and role are never accepted as identity claims. The session
store is deliberately placed outside APP_CONFIG.storage_root, which is mounted
by the Studio API for static media compatibility.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from studio_core.core.config import APP_CONFIG
from studio_core.core.storage import get_json_item
from studio_core.services.auth_sessions import SessionManager, SessionStoreError


_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    user_id: str
    name: str
    role: str


def _session_manager() -> SessionManager:
    configured_root = os.getenv("BARIBUDOS_PRIVATE_ROOT", "").strip()
    if configured_root:
        private_root = Path(configured_root).expanduser().resolve()
    else:
        if APP_CONFIG.environment.lower() in {"production", "prod"}:
            raise SessionStoreError("BARIBUDOS_PRIVATE_ROOT must be configured outside public storage")
        private_root = (APP_CONFIG.project_root / ".private").resolve()

    storage_root = APP_CONFIG.storage_root.expanduser().resolve()
    try:
        private_root.relative_to(storage_root)
    except ValueError:
        pass
    else:
        raise SessionStoreError("private session root must not be inside public storage")

    return SessionManager(private_root / "auth-sessions.sqlite3")


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> AuthenticatedPrincipal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        session = _session_manager().resolve(credentials.credentials)
    except (SessionStoreError, OSError):
        raise HTTPException(status_code=503, detail="Serviço de autenticação indisponível.") from None

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_json_item("data/users.json", session["user_id"])
    if not user or not bool(user.get("is_active", True)):
        try:
            _session_manager().revoke(credentials.credentials)
        except (SessionStoreError, OSError):
            pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta inativa ou inexistente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthenticatedPrincipal(
        user_id=str(user.get("id", "")),
        name=str(user.get("name", "")),
        role=str(user.get("role", "viewer")),
    )


def require_roles(*allowed_roles: str):
    normalized = frozenset(str(role).strip().lower() for role in allowed_roles if str(role).strip())

    def dependency(principal: AuthenticatedPrincipal = Depends(get_current_principal)) -> AuthenticatedPrincipal:
        if principal.role.strip().lower() not in normalized:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente.")
        return principal

    return dependency
