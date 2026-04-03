from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from studio_core.services.saga_visual_set_service import (
    list_saga_visual_sets,
    replace_saga_visual_sets,
    update_saga_visual_set,
)

router = APIRouter(prefix="/saga-visual-sets", tags=["saga-visual-sets"])


class SagaVisualSetsReplacePayload(BaseModel):
    items: List[Dict[str, Any]] = Field(default_factory=list)


class SagaVisualSetPatchPayload(BaseModel):
    saga_slug: str | None = None
    display_name: str | None = None
    active: bool | None = None
    version: int | None = None
    source_of_truth: str | None = None
    slots: Dict[str, Any] | None = None
    rotation_policy: Dict[str, Any] | None = None


@router.get("")
def saga_visual_sets_list() -> Dict[str, Any]:
    return list_saga_visual_sets()


@router.put("")
def saga_visual_sets_replace(payload: SagaVisualSetsReplacePayload) -> Dict[str, Any]:
    try:
        return replace_saga_visual_sets(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{item_id}")
def saga_visual_sets_patch(item_id: str, payload: SagaVisualSetPatchPayload) -> Dict[str, Any]:
    try:
        return update_saga_visual_set(item_id, payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
