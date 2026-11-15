#!/usr/bin/env python3
"""Export the registered FastAPI route surface and its resolved dependency graph.

This is an evidence inventory, not an authorization implementation. Every route
is intentionally marked UNCLASSIFIED / DENY_BY_DEFAULT until a reviewed policy
maps it to a server-derived principal and permission and runtime tests prove it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


def callable_name(value: Any) -> str:
    if value is None:
        return "<none>"
    module = getattr(value, "__module__", None)
    name = getattr(value, "__qualname__", None) or getattr(value, "__name__", None)
    if name is None:
        cls = type(value)
        module, name = cls.__module__, cls.__qualname__
    return f"{module}.{name}" if module else str(name)


def dependency_tree(dependant: Any) -> dict[str, Any]:
    call = getattr(dependant, "call", None)
    children = getattr(dependant, "dependencies", None) or []
    scopes = getattr(dependant, "security_scopes", None) or []
    return {
        "call": callable_name(call),
        "security_scopes": sorted(str(scope) for scope in scopes),
        "dependencies": [dependency_tree(child) for child in children],
    }


def build_manifest(api_routes: Iterable[Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for route in api_routes:
        path = str(getattr(route, "path", ""))
        name = str(getattr(route, "name", ""))
        endpoint = getattr(route, "endpoint", None)
        dependant = getattr(route, "dependant", None)
        methods = sorted(str(method).upper() for method in (getattr(route, "methods", None) or []))
        for method in methods:
            records.append({
                "route_id": f"{method} {path}",
                "method": method,
                "path": path,
                "name": name,
                "operation_id": getattr(route, "operation_id", None),
                "tags": sorted(str(tag) for tag in (getattr(route, "tags", None) or [])),
                "endpoint": callable_name(endpoint),
                "dependencies": dependency_tree(dependant) if dependant is not None else {
                    "call": "<unavailable>", "security_scopes": [], "dependencies": []
                },
                "policy_status": "UNCLASSIFIED",
                "required_principal": None,
                "required_permission": None,
                "default_access": "DENY_BY_DEFAULT",
                "runtime_protection_verified": False,
            })
    records.sort(key=lambda item: (item["path"], item["method"], item["endpoint"]))
    ids = [item["route_id"] for item in records]
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    return {
        "schema_version": 1,
        "source": "FastAPI app.routes (APIRoute instances)",
        "authorization_claim": False,
        "note": (
            "Inventory only. Dependency presence does not prove authorization. "
            "UNCLASSIFIED means no approved policy is recorded; DENY_BY_DEFAULT "
            "is the required target policy, not proof that runtime currently denies access."
        ),
        "route_count": len(records),
        "duplicate_route_ids": duplicate_ids,
        "routes": records,
    }


def render_markdown(manifest: dict[str, Any]) -> str:
    routes = manifest["routes"]
    dependency_count = sum(
        len(item["dependencies"].get("dependencies", [])) for item in routes
    )
    lines = [
        "# Studio FastAPI runtime route manifest",
        "",
        "> Generated from the imported FastAPI application. This is an inventory, not proof of access control.",
        "",
        f"- Registered method/path entries: **{manifest['route_count']}**",
        f"- Top-level dependency edges: **{dependency_count}**",
        f"- Duplicate method/path IDs: **{len(manifest['duplicate_route_ids'])}**",
        "- Policy status: **UNCLASSIFIED for every route**",
        "- Required target: **DENY_BY_DEFAULT until an explicit server-side policy is reviewed**",
        "",
        "| Method | Path | Endpoint | Operation ID | Direct dependencies | Policy |",
        "|---|---|---|---|---:|---|",
    ]
    for item in routes:
        deps = item["dependencies"].get("dependencies", [])
        values = [
            item["method"], item["path"], item["endpoint"],
            str(item["operation_id"] or "—"), str(len(deps)), item["policy_status"],
        ]
        lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    lines.extend([
        "",
        "## Interpretation and required review",
        "",
        "- A dependency in this manifest is not automatically an authentication or authorization check.",
        "- Review the complete nested dependency tree and trace each endpoint into service and storage operations.",
        "- Record the trusted principal source, permission, project/IP scope, public/private decision and negative HTTP tests in the reviewed policy manifest.",
        "- Do not change a route to public based only on its name, tags or current lack of dependencies.",
        "- This generator does not alter application behaviour and does not install middleware.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()

    from fastapi.routing import APIRoute
    from studio_core.api.main import app

    api_routes = [route for route in app.routes if isinstance(route, APIRoute)]
    manifest = build_manifest(api_routes)
    if not manifest["route_count"]:
        raise SystemExit("No FastAPI APIRoute entries found; refusing to publish an empty manifest.")
    if manifest["duplicate_route_ids"]:
        raise SystemExit(
            "Duplicate method/path route IDs found: "
            + ", ".join(manifest["duplicate_route_ids"])
        )

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(manifest), encoding="utf-8")
    print(f"Exported {manifest['route_count']} FastAPI method/path entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
