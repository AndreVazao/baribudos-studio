from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.project_service import list_projects
from studio_core.services.publication_payload_builder import build_store_payload
from studio_core.services.publication_policy_service import evaluate_project_publication_policy

router = APIRouter(prefix="/store", tags=["storefront"])


def _load_all_projects() -> list[dict]:
    result = list_projects(None)
    if isinstance(result, dict):
        return result.get("projects", [])
    return []


def _eligible_projects() -> list[dict]:
    projects = _load_all_projects()
    allowed = []
    for project in projects:
        try:
            policy = evaluate_project_publication_policy(project)
        except Exception:
            continue
        if policy.get("eligible_for_storefront"):
            allowed.append(project)
    return allowed


@router.get("/product/{project_id}")
def store_product(project_id: str) -> dict:
    projects = _eligible_projects()
    project = next((p for p in projects if str(p.get("id")) == str(project_id)), None)

    if not project:
        raise HTTPException(status_code=404, detail="project_not_found_or_not_public")

    payload = build_store_payload(project)
    return {"ok": True, "product": payload}


@router.get("/catalog")
def store_catalog() -> dict:
    projects = _eligible_projects()
    catalog = []
    for project in projects:
        try:
            catalog.append(build_store_payload(project))
        except Exception:
            continue
    return {"ok": True, "count": len(catalog), "products": catalog}


@router.get("/ip/{ip_slug}")
def store_ip(ip_slug: str) -> dict:
    projects = _eligible_projects()
    products = []
    for project in projects:
        if str(project.get("saga_slug") or "") == str(ip_slug):
            try:
                products.append(build_store_payload(project))
            except Exception:
                continue
    return {"ok": True, "ip_slug": ip_slug, "count": len(products), "products": products}


@router.get("/highlights")
def store_highlights() -> dict:
    projects = _eligible_projects()
    highlights = []
    for project in projects[:6]:
        try:
            highlights.append(build_store_payload(project))
        except Exception:
            continue
    return {"ok": True, "count": len(highlights), "highlights": highlights}
