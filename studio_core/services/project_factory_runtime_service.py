from __future__ import annotations

from typing import Dict, Any

from studio_core.services.ip_runtime_service import load_ip_runtime


def load_project_factory_context(
    ip_slug: str,
    project_payload: Dict[str, Any]
) -> Dict[str, Any]:

    ip_runtime = load_ip_runtime(ip_slug)

    return {
        "ip": ip_runtime["ip"],
        "slug": ip_runtime["slug"],
        "name": ip_runtime["name"],
        "default_language": ip_runtime["default_language"],
        "output_languages": ip_runtime["output_languages"],
        "palette": ip_runtime["palette"],
        "brand_assets": ip_runtime["brand_assets"],
        "canons": ip_runtime["canons"],
        "main_characters": ip_runtime["main_characters"],
        "project_payload": project_payload,
  }
