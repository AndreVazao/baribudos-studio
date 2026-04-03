from __future__ import annotations

from typing import Any, Dict, List

from studio_core.services.website_contract_validator import validate_project_website_contract


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def evaluate_project_publication_policy(project: Dict[str, Any]) -> Dict[str, Any]:
    project = _safe_dict(project)
    reasons: List[str] = []

    ready_for_publish = bool(project.get("ready_for_publish", False))
    if not ready_for_publish:
        reasons.append("ready_for_publish_false")

    publication_package = _safe_dict(project.get("publication_package", {}))
    has_frozen_package = bool(publication_package)
    if not has_frozen_package:
        reasons.append("publication_package_not_frozen")

    frozen_at = _safe_text(project.get("publication_package_frozen_at"))
    if not frozen_at:
        reasons.append("publication_package_frozen_at_missing")

    contract = {
        "status": "red",
        "required_ok": False,
        "seo_ok": False,
        "score_percent": 0,
        "missing_required_fields": [],
        "missing_required_assets": [],
        "missing_seo_fields": [],
        "label": "Website contract indisponível",
    }

    try:
        contract = validate_project_website_contract(project)
    except Exception:
        reasons.append("website_contract_validation_failed")
    else:
        if not bool(contract.get("required_ok", False)):
            reasons.append("website_contract_required_incomplete")
        if _safe_text(contract.get("status")) != "green":
            reasons.append(f"website_contract_status_{_safe_text(contract.get('status')) or 'unknown'}")

    eligible_for_storefront = bool(
        ready_for_publish
        and has_frozen_package
        and bool(frozen_at)
        and bool(contract.get("required_ok", False))
        and _safe_text(contract.get("status")) == "green"
    )

    label = "Elegível para storefront/publicação" if eligible_for_storefront else "Ainda não elegível para storefront/publicação"

    return {
        "ok": True,
        "project_id": _safe_text(project.get("id")),
        "ready_for_publish": ready_for_publish,
        "has_frozen_package": has_frozen_package,
        "publication_package_frozen_at": frozen_at,
        "contract": {
            "status": _safe_text(contract.get("status")),
            "label": _safe_text(contract.get("label")),
            "required_ok": bool(contract.get("required_ok", False)),
            "seo_ok": bool(contract.get("seo_ok", False)),
            "score_percent": int(contract.get("score_percent", 0) or 0),
            "missing_required_fields": contract.get("missing_required_fields", []),
            "missing_required_assets": contract.get("missing_required_assets", []),
            "missing_seo_fields": contract.get("missing_seo_fields", []),
        },
        "eligible_for_storefront": eligible_for_storefront,
        "eligible_for_website_publish": eligible_for_storefront,
        "label": label,
        "reasons": reasons,
    }
