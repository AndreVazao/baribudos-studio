from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from studio_core.services.auth_principal import AuthenticatedPrincipal, require_roles
from studio_core.services.pairing_service import create_pairing, list_pairings, resolve_pairing, revoke_pairing
router = APIRouter(prefix="/pairing", tags=["pairing"])
class PairingCreatePayload(BaseModel):
    pc_name: str
    lan_host: str
    remote_host: Optional[str] = ""
@router.get("")
def pairing_list(principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin"))) -> dict:
    return list_pairings()
@router.post("/create")
def pairing_create(payload: PairingCreatePayload, principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin"))) -> dict:
    return create_pairing(pc_name=payload.pc_name, lan_host=payload.lan_host, remote_host=payload.remote_host or "", created_by=principal.user_id)
@router.get("/resolve/{pair_code}")
def pairing_resolve(pair_code: str) -> dict:
    # The expiring high-entropy code is the device-pairing capability.
    return resolve_pairing(pair_code)
@router.post("/revoke/{pair_code}")
def pairing_revoke(pair_code: str, principal: AuthenticatedPrincipal = Depends(require_roles("owner", "admin"))) -> dict:
    return revoke_pairing(pair_code)
