from fastapi import APIRouter
from studio_core.services.asset_registry_service import get_assets

router = APIRouter(prefix="/api/public")


@router.get("/ip/{ip_slug}/assets")
def ip_assets(ip_slug: str):
    assets = get_assets({"ip_slug": ip_slug, "status": "published"})

    return {
        "ok": True,
        "ip_slug": ip_slug,
        "assets": assets
    }


@router.get("/assets")
def assets_by_context(context: str, ip_slug: str = None):
    filters = {"context": context, "status": "published"}
    if ip_slug:
        filters["ip_slug"] = ip_slug

    assets = get_assets(filters)

    return {
        "ok": True,
        "context": context,
        "assets": assets
    }


@router.get("/project/{project_id}/assets")
def project_assets(project_id: str):
    assets = get_assets({
        "project_id": project_id,
        "status": "published"
    })

    return {
        "ok": True,
        "project_id": project_id,
        "assets": assets
}
