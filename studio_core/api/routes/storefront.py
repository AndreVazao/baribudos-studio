from __future__ import annotations

from fastapi import APIRouter

from studio_core.services.project_service import list_projects
from studio_core.services.publication_payload_builder import build_store_payload


router = APIRouter(prefix="/store", tags=["storefront"])


# ==========================================================
# PRODUCT PAGE
# ==========================================================
@router.get("/product/{project_id}")
def store_product(project_id: str):
    projects = list_projects(None).get("projects", [])

    project = next((p for p in projects if p["id"] == project_id), None)

    if not project:
        return {"ok": False, "error": "project_not_found"}

    payload = build_store_payload(project)

    return {
        "ok": True,
        "product": payload
    }


# ==========================================================
# CATALOG
# ==========================================================
@router.get("/catalog")
def store_catalog():
    projects = list_projects(None).get("projects", [])

    catalog = []

    for project in projects:
        try:
            catalog.append(build_store_payload(project))
        except Exception:
            continue

    return {
        "ok": True,
        "count": len(catalog),
        "products": catalog
    }


# ==========================================================
# IP STORE PAGE
# ==========================================================
@router.get("/ip/{ip_slug}")
def store_ip(ip_slug: str):
    projects = list_projects(None).get("projects", [])

    products = []

    for project in projects:
        if project.get("saga_slug") == ip_slug:
            try:
                products.append(build_store_payload(project))
            except Exception:
                continue

    return {
        "ok": True,
        "ip_slug": ip_slug,
        "count": len(products),
        "products": products
    }


# ==========================================================
# HOMEPAGE HIGHLIGHTS
# ==========================================================
@router.get("/highlights")
def store_highlights():
    projects = list_projects(None).get("projects", [])

    highlights = []

    for project in projects[:6]:
        try:
            highlights.append(build_store_payload(project))
        except Exception:
            continue

    return {
        "ok": True,
        "highlights": highlights
  }
