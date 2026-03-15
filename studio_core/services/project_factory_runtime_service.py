from __future__ import annotations

from typing import Dict, Any

from studio_core.services.saga_runtime_service import load_saga_runtime


def load_project_factory_context(
    ip_slug: str,
    project_payload: Dict[str, Any]
) -> Dict[str, Any]:
    runtime = load_saga_runtime(ip_slug)

    return {
        "ip": {
            "id": runtime.get("id", ""),
            "slug": runtime.get("slug", ""),
            "name": runtime.get("name", ""),
            "owner_id": runtime.get("owner_id", ""),
            "owner_name": runtime.get("owner_name", ""),
        },
        "slug": runtime.get("slug", ""),
        "name": runtime.get("name", ""),
        "default_language": runtime.get("default_language", "pt-PT"),
        "output_languages": runtime.get("output_languages", ["pt-PT"]),
        "metadata": runtime.get("metadata", {}),
        "palette": runtime.get("palette", {}),
        "brand_assets": runtime.get("brand_assets", {}),
        "permissions": runtime.get("permissions", {}),
        "canons": runtime.get("canons", {}),
        "resolved": runtime.get("resolved", {}),
        "validation": runtime.get("validation", {}),
        "main_characters": runtime.get("main_characters", []),
        "project_payload": project_payload,
    }
