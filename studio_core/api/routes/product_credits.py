from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.product_credits_service import (
    get_product_credits,
    patch_product_credits,
    rebuild_product_credits,
)

router = APIRouter(prefix="/product-credits", tags=["product-credits"])


@router.get("/{project_id}")
def get_credits(project_id: str) -> dict:
    try:
        return {
            "ok": True,
            "product_credits": get_product_credits(project_id),
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{project_id}/rebuild")
def rebuild_credits(project_id: str) -> dict:
    try:
        return rebuild_product_credits(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{project_id}")
def patch_credits(project_id: str, payload: dict | None = None) -> dict:
    try:
        return patch_product_credits(project_id, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
