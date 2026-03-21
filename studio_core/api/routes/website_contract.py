from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.project_service import list_projects
from studio_core.services.website_contract_validator import (
    validate_project_website_contract,
)

router = APIRouter(prefix="/website-contract", tags=["website-contract"])


def _load_all_projects() -> list[dict]:
    result = list_projects(None)
    if isinstance(result, dict):
        return result.get("projects", [])
    return []


@router.get("/validate/{project_id}")
def validate_website_contract(project_id: str) -> dict:
    projects = _load_all_projects()
    project = next((item for item in projects if str(item.get("id")) == str(project_id)), None)

    if not project:
      raise HTTPException(status_code=404, detail="project_not_found")

    return validate_project_website_contract(project)


@router.get("/validate-all")
def validate_all_website_contracts() -> dict:
    projects = _load_all_projects()

    results = []
    for project in projects:
        try:
            results.append(validate_project_website_contract(project))
        except Exception as exc:
            results.append({
                "ok": False,
                "project_id": project.get("id"),
                "error": str(exc),
            })

    green = len([item for item in results if item.get("status") == "green"])
    yellow = len([item for item in results if item.get("status") == "yellow"])
    red = len([item for item in results if item.get("status") == "red"])

    return {
        "ok": True,
        "count": len(results),
        "summary": {
            "green": green,
            "yellow": yellow,
            "red": red,
        },
        "results": results,
}
