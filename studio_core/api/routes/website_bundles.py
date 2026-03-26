from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from studio_core.services.website_bundle_service import (
    get_website_bundles_status,
    publish_commerce_group_to_website,
)

router = APIRouter(prefix="/website-bundles", tags=["website-bundles"])


@router.post("/publish/{group_id}")
def website_bundles_publish(group_id: str) -> Dict[str, Any]:
    try:
        return publish_commerce_group_to_website(group_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/status")
def website_bundles_status(limit: int = Query(default=20, ge=1, le=100)) -> Dict[str, Any]:
    try:
        return {
            "ok": True,
            "website": get_website_bundles_status(limit=limit),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
