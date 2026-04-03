from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from studio_core.services.commerce_group_service import (
    create_commerce_group,
    delete_commerce_group,
    list_commerce_groups,
    update_commerce_group,
)

router = APIRouter(prefix="/commerce-groups", tags=["commerce-groups"])


class CommerceGroupItemPayload(BaseModel):
    product_id: str = ""
    slug: str = ""
    title: str = ""
    type: str = ""
    currency: str = "EUR"
    price_cents: int = 0
    position: int = 0


class CommerceGroupCreatePayload(BaseModel):
    slug: str
    name: str
    description: str = ""
    group_type: str = "bundle"
    currency: str = "EUR"
    price_cents: int = 0
    active: bool = False
    featured: bool = False
    items: List[CommerceGroupItemPayload] = Field(default_factory=list)


class CommerceGroupPatchPayload(BaseModel):
    name: str | None = None
    description: str | None = None
    group_type: str | None = None
    currency: str | None = None
    price_cents: int | None = None
    active: bool | None = None
    featured: bool | None = None
    items: List[CommerceGroupItemPayload] | None = None


@router.get("")
def commerce_groups_list() -> Dict[str, Any]:
    return list_commerce_groups()


@router.post("")
def commerce_groups_create(payload: CommerceGroupCreatePayload) -> Dict[str, Any]:
    try:
        return {
            "ok": True,
            "group": create_commerce_group(payload.model_dump()),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{group_id}")
def commerce_groups_patch(group_id: str, payload: CommerceGroupPatchPayload) -> Dict[str, Any]:
    try:
        return {
            "ok": True,
            "group": update_commerce_group(group_id, payload.model_dump(exclude_none=True)),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{group_id}")
def commerce_groups_delete(group_id: str) -> Dict[str, Any]:
    return {
        "ok": True,
        "result": delete_commerce_group(group_id),
    }
