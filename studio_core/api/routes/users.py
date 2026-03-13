from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import User, UserCreate, UserPatch, UserPinPatch, now_iso
from studio_core.core.storage import (
    append_json_item,
    list_json_items,
    update_json_item,
)

router = APIRouter(prefix="/users", tags=["users"])

USERS_FILE = "data/users.json"


def ensure_default_owner() -> None:
    users = list_json_items(USERS_FILE)
    if users:
        return

    owner = User(
        name="André",
        role="owner",
        pin="1234",
        is_active=True
    )
    append_json_item(USERS_FILE, owner.model_dump())


@router.get("")
def list_users() -> dict:
    ensure_default_owner()
    return {"ok": True, "users": list_json_items(USERS_FILE)}


@router.post("")
def create_user(payload: UserCreate) -> dict:
    ensure_default_owner()

    user = User(
        name=payload.name.strip(),
        role=payload.role,
        pin=payload.pin.strip(),
        is_active=payload.is_active,
    )
    append_json_item(USERS_FILE, user.model_dump())
    return {"ok": True, "user": user.model_dump()}


@router.patch("/{user_id}")
def patch_user(user_id: str, payload: UserPatch) -> dict:
    ensure_default_owner()

    def updater(current: dict) -> dict:
        updated = {
            **current,
            "updated_at": now_iso(),
        }

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

    return {"ok": True, "user": user}


@router.patch("/{user_id}/pin")
def patch_user_pin(user_id: str, payload: UserPinPatch) -> dict:
    ensure_default_owner()

    def updater(current: dict) -> dict:
        return {
            **current,
            "pin": payload.pin.strip(),
            "updated_at": now_iso(),
        }

    try:
        user = update_json_item(USERS_FILE, user_id, updater)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"ok": True, "user": user}


@router.post("/login")
def login(payload: dict) -> dict:
    ensure_default_owner()

    name = str(payload.get("name", "")).strip().lower()
    pin = str(payload.get("pin", "")).strip()

    for user in list_json_items(USERS_FILE):
        if (
            str(user.get("name", "")).strip().lower() == name
            and str(user.get("pin", "")).strip() == pin
            and bool(user.get("is_active", True))
        ):
            return {"ok": True, "user": user}

    raise HTTPException(status_code=401, detail="Credenciais inválidas.")
