from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from studio_core.services.website_visual_set_service import (
    export_saga_visual_sets_payload,
    get_website_visual_sets_status,
    publish_all_saga_visual_sets_to_website,
    publish_saga_visual_set_to_website,
)

router = APIRouter(prefix="/website-visual-sets", tags=["website-visual-sets"])


@router.get("/export")
def website_visual_sets_export() -> Dict[str, Any]:
    return export_saga_visual_sets_payload()


@router.get("/status")
def website_visual_sets_status() -> Dict[str, Any]:
    try:
        return get_website_visual_sets_status()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/publish/{item_id}")
def website_visual_sets_publish(item_id: str) -> Dict[str, Any]:
    try:
        return publish_saga_visual_set_to_website(item_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/publish-all")
def website_visual_sets_publish_all() -> Dict[str, Any]:
    try:
        return publish_all_saga_visual_sets_to_website()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
