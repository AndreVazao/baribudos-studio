from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from studio_core.services.deploy_control_service import (
    get_vercel_website_summary,
    list_vercel_website_deployments,
)

router = APIRouter(prefix="/deploy-control", tags=["deploy-control"])


@router.get("/vercel/summary")
def deploy_control_vercel_summary() -> dict:
    try:
        return {
            "ok": True,
            "deploy": get_vercel_website_summary(),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/vercel/deployments")
def deploy_control_vercel_deployments(
    limit: int = Query(default=10, ge=1, le=50),
) -> dict:
    try:
        return {
            "ok": True,
            "deploy": list_vercel_website_deployments(limit=limit),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
