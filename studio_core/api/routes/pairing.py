from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from studio_core.services.pairing_service import (
    create_pairing,
    list_pairings,
    resolve_pairing,
    revoke_pairing,
)

router = APIRouter(prefix="/pairing", tags=["pairing"])


class PairingCreatePayload(BaseModel):
    pc_name: str
    lan_host: str
    remote_host: Optional[str] = ""
    created_by: Optional[str] = ""


@router.get("")
def pairing_list() -> dict:
    return list_pairings()


@router.post("/create")
def pairing_create(payload: PairingCreatePayload) -> dict:
    return create_pairing(
        pc_name=payload.pc_name,
        lan_host=payload.lan_host,
        remote_host=payload.remote_host or "",
        created_by=payload.created_by or "",
    )


@router.get("/resolve/{pair_code}")
def pairing_resolve(pair_code: str) -> dict:
    return resolve_pairing(pair_code)


@router.post("/revoke/{pair_code}")
def pairing_revoke(pair_code: str) -> dict:
    return revoke_pairing(pair_code)
