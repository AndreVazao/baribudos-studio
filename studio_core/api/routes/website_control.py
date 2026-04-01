from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.website_control_service import (
    get_website_catalog_status,
    get_website_health_status,
    get_website_publication_divergence,
    get_website_publication_status,
    get_website_summary_status,
)

router = APIRouter(prefix="/website-control", tags=["website-control"])


@router.get("/health")
def website_control_health() -> dict:
    try:
        return {"ok": True, "website": get_website_health_status()}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/summary")
def website_control_summary() -> dict:
    try:
        return {"ok": True, "website": get_website_summary_status()}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/catalog")
def website_control_catalog(limit: int = 25, active_only: bool = False) -> dict:
    try:
        return {"ok": True, "website": get_website_catalog_status(limit=limit, active_only=active_only)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/publication/{publication_id}")
def website_control_publication(publication_id: str) -> dict:
    try:
        return {"ok": True, "website": get_website_publication_status(publication_id)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/divergence/{publication_id}")
def website_control_divergence(publication_id: str, expected_checksum: str = "", expected_project_version: str = "") -> dict:
    try:
        return {"ok": True, "website": get_website_publication_divergence(publication_id, expected_checksum=expected_checksum, expected_project_version=expected_project_version)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
