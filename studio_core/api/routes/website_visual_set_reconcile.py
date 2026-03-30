from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from studio_core.services.website_visual_set_reconcile_service import get_visual_set_reconcile_report

router = APIRouter(prefix="/website-visual-sets-reconcile", tags=["website-visual-sets-reconcile"])


@router.get("")
def website_visual_set_reconcile() -> Dict[str, Any]:
    try:
        return get_visual_set_reconcile_report()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
