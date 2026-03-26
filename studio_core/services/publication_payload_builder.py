from __future__ import annotations

from typing import Any, Dict

from studio_core.services.website_contract_payload_service import build_website_payload


def build_store_payload(project: Dict[str, Any]) -> Dict[str, Any]:
    return build_website_payload(project)
