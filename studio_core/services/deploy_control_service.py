from __future__ import annotations

import json
import os
from typing import Any, Dict, List
from urllib import error, parse, request


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _api_token() -> str:
    token = _normalize_text(os.getenv("BARIBUDOS_VERCEL_API_TOKEN"))
    if not token:
        raise ValueError("vercel_api_token_missing")
    return token


def _team_id() -> str:
    team_id = _normalize_text(os.getenv("BARIBUDOS_VERCEL_TEAM_ID"))
    if not team_id:
        raise ValueError("vercel_team_id_missing")
    return team_id


def _website_project_id() -> str:
    project_id = _normalize_text(os.getenv("BARIBUDOS_VERCEL_PROJECT_ID_WEBSITE"))
    if not project_id:
        raise ValueError("vercel_project_id_website_missing")
    return project_id


def _vercel_get(path: str, query: Dict[str, Any] | None = None) -> Dict[str, Any]:
    qs = parse.urlencode({key: value for key, value in (query or {}).items() if value not in {None, ""}})
    url = f"https://api.vercel.com{path}"
    if qs:
        url = f"{url}?{qs}"

    http_request = request.Request(
        url,
        headers={
            "Authorization": f"Bearer {_api_token()}",
            "Content-Type": "application/json",
        },
        method="GET",
    )

    try:
        with request.urlopen(http_request, timeout=20) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        raise ValueError(f"vercel_http_error:{exc.code}:{details}") from exc
    except error.URLError as exc:
        raise ValueError(f"vercel_connection_error:{exc.reason}") from exc


def _compact_deployment(item: Dict[str, Any]) -> Dict[str, Any]:
    meta = item.get("meta") if isinstance(item.get("meta"), dict) else {}
    creator = item.get("creator") if isinstance(item.get("creator"), dict) else {}
    return {
        "id": item.get("id", ""),
        "name": item.get("name", ""),
        "url": item.get("url", ""),
        "state": item.get("state", ""),
        "target": item.get("target"),
        "created": item.get("created"),
        "creator": {
            "username": creator.get("username", ""),
            "email": creator.get("email", ""),
        },
        "git": {
            "repo": meta.get("githubRepo", ""),
            "ref": meta.get("githubCommitRef", ""),
            "sha": meta.get("githubCommitSha", ""),
            "message": meta.get("githubCommitMessage", ""),
            "author": meta.get("githubCommitAuthorName", ""),
        },
        "inspector_url": item.get("inspectorUrl", ""),
        "is_rollback_candidate": bool(item.get("isRollbackCandidate", False)),
    }


def get_vercel_website_summary() -> Dict[str, Any]:
    team_id = _team_id()
    project_id = _website_project_id()

    project = _vercel_get(f"/v9/projects/{project_id}", {"teamId": team_id})
    deployments_payload = _vercel_get("/v6/deployments", {"projectId": project_id, "teamId": team_id, "limit": 10})

    deployments_raw = deployments_payload.get("deployments", []) if isinstance(deployments_payload.get("deployments"), list) else []
    latest = project.get("latestDeployment") if isinstance(project.get("latestDeployment"), dict) else {}

    return {
        "ok": True,
        "provider": "vercel",
        "team_id": team_id,
        "project": {
            "id": project.get("id", ""),
            "name": project.get("name", ""),
            "framework": project.get("framework", ""),
            "node_version": project.get("nodeVersion", ""),
            "created_at": project.get("createdAt"),
            "updated_at": project.get("updatedAt"),
            "domains": project.get("domains", []) if isinstance(project.get("domains"), list) else [],
            "live": bool(project.get("live", False)),
        },
        "latest_deployment": {
            "id": latest.get("id", ""),
            "url": latest.get("url", ""),
            "created_at": latest.get("createdAt"),
            "ready_state": latest.get("readyState", ""),
            "target": latest.get("target"),
        },
        "deployments": [_compact_deployment(item) for item in deployments_raw],
    }


def list_vercel_website_deployments(limit: int = 10) -> Dict[str, Any]:
    team_id = _team_id()
    project_id = _website_project_id()
    capped_limit = max(1, min(int(limit), 50))

    payload = _vercel_get("/v6/deployments", {"projectId": project_id, "teamId": team_id, "limit": capped_limit})
    deployments_raw = payload.get("deployments", []) if isinstance(payload.get("deployments"), list) else []
    pagination = payload.get("pagination", {}) if isinstance(payload.get("pagination"), dict) else {}

    return {
        "ok": True,
        "provider": "vercel",
        "team_id": team_id,
        "project_id": project_id,
        "count": len(deployments_raw),
        "pagination": pagination,
        "deployments": [_compact_deployment(item) for item in deployments_raw],
    }
