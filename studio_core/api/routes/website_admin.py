from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from studio_core.services.website_admin_service import (
    update_website_product_pricing,
    update_website_product_visibility,
)

router = APIRouter(prefix="/website-admin", tags=["website-admin"])


class ProductVisibilityPayload(BaseModel):
    active: bool | None = None
    featured: bool | None = None


class ProductPricingPayload(BaseModel):
    price_cents: int
    currency: str = "EUR"


@router.patch("/products/{product_id}/visibility")
def website_admin_product_visibility(product_id: str, payload: ProductVisibilityPayload) -> dict:
    try:
        return {
            "ok": True,
            "website": update_website_product_visibility(
                product_id=product_id,
                active=payload.active,
                featured=payload.featured,
            ),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/products/{product_id}/pricing")
def website_admin_product_pricing(product_id: str, payload: ProductPricingPayload) -> dict:
    try:
        return {
            "ok": True,
            "website": update_website_product_pricing(
                product_id=product_id,
                price_cents=payload.price_cents,
                currency=payload.currency,
            ),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
