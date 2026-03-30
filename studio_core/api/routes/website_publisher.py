from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.website_publisher_service import (
    build_publish_envelope,
    get_project_publish_status,
    publish_project_to_website,
)

router = APIRouter(prefix="/website-publisher", tags=["website-publisher"])


@router.get("/envelope/{project_id}")
def website_publish_envelope(project_id: str) -> dict:
    try:
        envelope = build_publish_envelope(project_id)
        return {
            "ok": True,
            "project_id": project_id,
            "envelope": envelope,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/publish/{project_id}")
def website_publish(project_id: str) -> dict:
    try:
        return publish_project_to_website(project_id)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if message == "project_not_found" else 400
        raise HTTPException(status_code=status_code, detail=message) from exc


@router.get("/status/{project_id}")
def website_publish_status(project_id: str) -> dict:
    try:
        return get_project_publish_status(project_id)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if message == "project_not_found" else 400
        raise HTTPException(status_code=status_code, detail=message) from exc
