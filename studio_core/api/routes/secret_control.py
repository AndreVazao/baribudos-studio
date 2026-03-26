from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from studio_core.services.secret_control_service import (
    create_secret_vault,
    delete_secret_vault,
    export_secret_vault,
    get_secret_vault,
    list_secret_vaults,
    update_secret_vault,
)

router = APIRouter(prefix="/secret-control", tags=["secret-control"])


class SecretVaultCreatePayload(BaseModel):
    name: str
    target: str = "custom"
    environment: str = "local"
    file_name: str = ".env"
    raw_text: str = ""
    notes: str = ""


class SecretVaultPatchPayload(BaseModel):
    name: str | None = None
    target: str | None = None
    environment: str | None = None
    file_name: str | None = None
    raw_text: str | None = None
    notes: str | None = None
    rows: List[Dict[str, Any]] | None = Field(default=None)


@router.get("/vaults")
def secret_control_vaults() -> Dict[str, Any]:
    return list_secret_vaults()


@router.get("/vault/{vault_id}")
def secret_control_vault(vault_id: str, reveal_values: bool = Query(default=False)) -> Dict[str, Any]:
    try:
        return {
            "ok": True,
            "vault": get_secret_vault(vault_id, reveal_values=reveal_values),
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/vaults")
def secret_control_create(payload: SecretVaultCreatePayload) -> Dict[str, Any]:
    try:
        return {
            "ok": True,
            "vault": create_secret_vault(payload.model_dump()),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/vault/{vault_id}")
def secret_control_patch(vault_id: str, payload: SecretVaultPatchPayload) -> Dict[str, Any]:
    try:
        return {
            "ok": True,
            "vault": update_secret_vault(vault_id, payload.model_dump(exclude_none=True)),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/vault/{vault_id}")
def secret_control_delete(vault_id: str) -> Dict[str, Any]:
    return {
        "ok": True,
        "result": delete_secret_vault(vault_id),
    }


@router.get("/export/{vault_id}")
def secret_control_export(vault_id: str) -> Dict[str, Any]:
    try:
        return export_secret_vault(vault_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
