from __future__ import annotations

from typing import Dict, Any

from studio_core.services.project_factory_engine import build_factory_context


def load_project_factory_context(
    ip_slug: str,
    project_payload: Dict[str, Any]
) -> Dict[str, Any]:
    return build_factory_context(ip_slug=ip_slug, project_payload=project_payload)
