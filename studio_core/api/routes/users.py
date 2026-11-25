from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.security import HTTPBearer

from studio_core.core.models import User, UserCreate, UserPatch, UserPinPatch, now_iso
from studio_core.core.storage import (
    append_json_item,
    list_json_items,
    update_json_item,
)
from studio_core.services.auth_credentials import hash_pin, verify_pin, is_hashed_pin
from studio_core.services.auth_principal import _session_manager

router = APIRouter(prefix="/users", tags=["users"])
USERS_FILE = "data/users.json"
_bearer = HTTPBearer(auto_error=False)


def public_user(user: dict) -> dict:
    allowed = ("id", "name", "role", "is_active", "created_at", "updated_at")
    return {key: user[key] for key in allowed if key in user}


def ensure_default_owner() -> None:
    users = list_json_items(USERS_FILE)
    if users:
        return
    owner = User(name="André", role="owner", pin="1234", is_active=True)
    append_json_item(USERS_FILE, owner.model_dump())


@router.get("")
def list_users() -> dict:
    ensure_default_owner()
    return {"ok": True, "users": [public_user(user) for user in list_json_items(USERS_FILE)]}


@router.post("")
def create_user(payload: UserCreate) -> dict:
    ensure_default_owner()
    user = User(name=payload.name.strip(), role=payload.role, pin=hash_pin(payload.pin.strip()), is_active=payload.is_active)
    append_json_item(USERS_FILE, user.model_dump())
    return {"ok": True, "user": public_user(user.model_dump())}


@router.patch("/{user_id}")
def patch_user(user_id: str, payload: UserPatch) -> dict:
    ensure_default_owner()
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
    ensure_default_owner()
    def updater(current: dict) -> dict:
        return {**current, "pin": hash_pin(payload.pin.strip()), "updated_at": now_iso()}
    try:
        user = update_json_item(USERS_FILE, user_id, updater)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "user": public_user(user)}


@router.post("/login")
def login(payload: dict) -> dict:
    ensure_default_owner()
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
