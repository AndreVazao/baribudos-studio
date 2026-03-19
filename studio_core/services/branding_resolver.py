from studio_core.services.asset_registry_service import get_assets


def resolveBrandAssets(context, ip_slug=None, project_id=None):
    if context == "global":
        return get_assets({
            "asset_type": "studio_logo",
            "is_primary": True,
            "status": "published"
        })

    if context == "ip":
        return get_assets({
            "asset_type": "ip_logo",
            "ip_slug": ip_slug,
            "is_primary": True,
            "status": "published"
        })

    if context == "product":
        return get_assets({
            "project_id": project_id,
            "asset_type": "cover",
            "is_primary": True,
            "status": "published"
        })

    return []
