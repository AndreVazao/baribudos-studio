from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import hmac

from studio_core.core.models import User, UserCreate, UserPatch, UserPinPatch, now_iso
from studio_core.core.storage import (
    append_json_item,
    list_json_items,
    update_json_item,
)
from studio_core.services.auth_credentials import hash_pin, verify_pin, is_hashed_pin
from pathlib import Path
import os

from studio_core.core.config import APP_CONFIG
from studio_core.services.auth_sessions import SessionManager, SessionStoreError

router = APIRouter(prefix="/users", tags=["users"])
USERS_FILE = "data/users.json"


def _private_root() -> Path:
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
        raise SessionStoreError("private root must not be inside public storage")
    private_root.mkdir(parents=True, exist_ok=True)
    return private_root


def _session_manager() -> SessionManager:
    return SessionManager(_private_root() / "auth-sessions.sqlite3")


def public_user(user: dict) -> dict:
    allowed = ("id", "name", "role", "is_active", "created_at", "updated_at")
    return {key: user[key] for key in allowed if key in user}


class OwnerBootstrapPayload(BaseModel):
    bootstrap_token: str = Field(min_length=32, max_length=4096)
    name: str = Field(min_length=1, max_length=120)
    pin: str = Field(min_length=1, max_length=20)



@router.get("")
def list_users() -> dict:
    return {"ok": True, "users": [public_user(user) for user in list_json_items(USERS_FILE)]}


@router.post("/bootstrap")
def bootstrap_owner(payload: OwnerBootstrapPayload) -> dict:
    """Create the first owner only when a deployment-provided one-time token is configured."""
    configured_token = os.getenv("BARIBUDOS_BOOTSTRAP_TOKEN", "").strip()
    if len(configured_token) < 32:
        raise HTTPException(status_code=503, detail="Bootstrap inicial não está configurado.")
    if not hmac.compare_digest(payload.bootstrap_token, configured_token):
        raise HTTPException(status_code=401, detail="Token de bootstrap inválido.")

    name, pin = payload.name.strip(), payload.pin.strip()
    if not name or not pin:
        raise HTTPException(status_code=422, detail="Nome e PIN são obrigatórios.")

    lock_path = _private_root() / "owner-bootstrap.lock"
    try:
        lock_fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise HTTPException(status_code=409, detail="Bootstrap em curso; tente novamente.") from None
    except (OSError, RuntimeError):
        raise HTTPException(status_code=503, detail="Bootstrap inicial indisponível.") from None

    try:
        if list_json_items(USERS_FILE):
            raise HTTPException(status_code=409, detail="Bootstrap já concluído.")
        owner = User(name=name, role="owner", pin=hash_pin(pin), is_active=True)
        append_json_item(USERS_FILE, owner.model_dump())
        try:
            session = _session_manager().create(owner.id)
        except (RuntimeError, OSError, ValueError):
            raise HTTPException(status_code=503, detail="Owner criado, mas sessão indisponível; faça login.") from None
        return {"ok": True, "user": public_user(owner.model_dump()), "session": session}
    finally:
        os.close(lock_fd)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


@router.post("")
def create_user(payload: UserCreate) -> dict:
    name = payload.name.strip()
    pin = payload.pin.strip()
    if not name or not pin:
        raise HTTPException(status_code=422, detail="Nome e PIN são obrigatórios.")
    user = User(name=name, role=payload.role, pin=hash_pin(pin), is_active=payload.is_active)
    append_json_item(USERS_FILE, user.model_dump())
    return {"ok": True, "user": public_user(user.model_dump())}


@router.patch("/{user_id}")
def patch_user(user_id: str, payload: UserPatch) -> dict:
    def updater(current: dict) -> dict:
        updated = {**current, "updated_at": now_iso()}
        if payload.name is not None:
            updated["name"] = payload.name.strip()
        if payload.role is not None:
            updated["role"] = payload.role
        if payload.is_active is not None:
            updated["is_active"] = payload.is_active
        return updated
    try:
        user = update_json_item(USERS_FILE, user_id, updater)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "user": public_user(user)}


@router.patch("/{user_id}/pin")
def patch_user_pin(user_id: str, payload: UserPinPatch) -> dict:
    pin = payload.pin.strip()
    if not pin:
        raise HTTPException(status_code=422, detail="PIN obrigatório.")
    def updater(current: dict) -> dict:
        return {**current, "pin": hash_pin(pin), "updated_at": now_iso()}
    try:
        user = update_json_item(USERS_FILE, user_id, updater)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "user": public_user(user)}


@router.post("/login")
def login(payload: dict) -> dict:
    name = str(payload.get("name", "")).strip().lower()
    pin = str(payload.get("pin", "")).strip()
    if not name or not pin:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    for user in list_json_items(USERS_FILE):
        if str(user.get("name", "")).strip().lower() != name or not bool(user.get("is_active", True)):
            continue
        stored = user.get("pin")
        if not verify_pin(pin, stored if isinstance(stored, str) else ""):
            continue
        if not is_hashed_pin(stored):
            migrated_hash = hash_pin(pin)
            user_id = str(user.get("id", ""))
            try:
                user = update_json_item(USERS_FILE, user_id, lambda current: {
                    **current, "pin": migrated_hash, "updated_at": now_iso()
                })
            except ValueError:
                raise HTTPException(status_code=503, detail="Não foi possível migrar a credencial.") from None
        try:
            session = _session_manager().create(str(user.get("id", "")))
        except (RuntimeError, OSError, ValueError):
            raise HTTPException(status_code=503, detail="Serviço de autenticação indisponível.") from None
        return {"ok": True, "user": public_user(user), "session": session}

    raise HTTPException(status_code=401, detail="Credenciais inválidas.")


@router.get("/me")
def get_current_user(request: Request) -> dict:
    """Return the active public user attached to the presented server session."""
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    try:
        manager = _session_manager()
        resolved = manager.resolve(token.strip())
        if resolved is None:
            raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.")
        user_id = resolved.get("user_id", "")
        user = next((candidate for candidate in list_json_items(USERS_FILE)
                     if str(candidate.get("id", "")) == user_id), None)
        if user is None or not bool(user.get("is_active", True)):
            manager.revoke(token.strip())
            raise HTTPException(status_code=401, detail="Conta inativa ou inexistente.")
        return {"ok": True, "user": public_user(user), "session_expires_at": resolved.get("expires_at")}
    except HTTPException:
        raise
    except (RuntimeError, OSError, ValueError):
        raise HTTPException(status_code=503, detail="Serviço de autenticação indisponível.") from None


@router.post("/logout")
def logout(request: Request) -> dict:
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    try:
        revoked = _session_manager().revoke(token.strip())
    except (RuntimeError, OSError):
        raise HTTPException(status_code=503, detail="Serviço de autenticação indisponível.") from None
    if not revoked:
        raise HTTPException(status_code=401, detail="Sessão inválida.")
    return {"ok": True}
