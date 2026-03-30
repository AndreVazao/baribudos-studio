from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from studio_core.services.website_bundle_reconcile_service import get_bundle_reconcile_report

router = APIRouter(prefix="/website-bundles-reconcile", tags=["website-bundles-reconcile"])


@router.get("")
def website_bundle_reconcile(limit: int = Query(default=100, ge=1, le=100)) -> Dict[str, Any]:
    try:
        return get_bundle_reconcile_report(limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
