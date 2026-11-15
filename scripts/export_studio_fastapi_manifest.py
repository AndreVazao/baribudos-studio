#!/usr/bin/env python3
"""Export the registered FastAPI route surface and its resolved dependency graph.

This is an evidence inventory, not an authorization implementation. Every route
is intentionally marked UNCLASSIFIED / DENY_BY_DEFAULT until a reviewed policy
maps it to a server-derived principal and permission and runtime tests prove it.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

SAFE_CORS_OPTIONS = (
    "allow_origins",
    "allow_origin_regex",
    "allow_credentials",
    "allow_methods",
    "allow_headers",
    "expose_headers",
    "max_age",
)


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


def _json_safe_option(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, (list, tuple, set)):
        return [_json_safe_option(item) for item in value]
    return f"<{type(value).__name__}>"


def application_security_surface(app: Any) -> dict[str, Any]:
    """Describe app-wide dependencies and middleware without serializing secrets."""
    router = getattr(app, "router", None)
    raw_dependencies = getattr(router, "dependencies", None) or []
    global_dependencies = []
    for item in raw_dependencies:
        target = getattr(item, "dependency", None) or getattr(item, "call", None)
        scopes = getattr(item, "scopes", None) or getattr(item, "security_scopes", None) or []
        global_dependencies.append({
            "call": callable_name(target),
            "security_scopes": sorted(str(scope) for scope in scopes),
        })

    middleware_records = []
    for item in getattr(app, "user_middleware", None) or []:
        middleware_class = getattr(item, "cls", None)
        middleware_name = callable_name(middleware_class) if middleware_class else type(item).__qualname__
        options = getattr(item, "kwargs", None) or getattr(item, "options", None) or {}
        if not isinstance(options, dict):
            options = {}
        record = {
            "middleware": middleware_name,
            "option_names": sorted(str(key) for key in options),
        }
        if getattr(middleware_class, "__name__", "") == "CORSMiddleware":
            record["cors_options"] = {
                key: _json_safe_option(options[key])
                for key in SAFE_CORS_OPTIONS
                if key in options
            }
        middleware_records.append(record)

    return {
        "global_dependency_count": len(global_dependencies),
        "global_dependencies": global_dependencies,
        "middleware_count": len(middleware_records),
        "middleware": middleware_records,
        "authorization_claim": False,
    }


def non_api_route_inventory(all_routes: Iterable[Any], api_routes: Iterable[Any]) -> dict[str, Any]:
    """Inventory Starlette routes and mounts excluded from the APIRoute list."""
    api_ids = {id(route) for route in api_routes}
    records: list[dict[str, Any]] = []
    for route in all_routes:
        if id(route) in api_ids:
            continue
        mounted_app = getattr(route, 'app', None)
        record: dict[str, Any] = {
            'route_type': type(route).__name__,
            'path': str(getattr(route, 'path', '')),
            'name': str(getattr(route, 'name', '')),
            'methods': sorted(str(method).upper() for method in (getattr(route, 'methods', None) or [])),
        }
        if mounted_app is not None:
            mounted_type = type(mounted_app)
            record['mounted_app'] = f'{mounted_type.__module__}.{mounted_type.__qualname__}'
            if mounted_type.__name__ == 'StaticFiles':
                directory = getattr(mounted_app, 'directory', None)
                directory_path = Path(directory) if directory is not None else None
                record['static_files'] = {
                    'directory_configured': directory_path is not None,
                    'directory_exists': bool(directory_path and directory_path.is_dir()),
                    'html': bool(getattr(mounted_app, 'html', False)),
                    'check_dir': bool(getattr(mounted_app, 'check_dir', False)),
                    'follow_symlink': bool(getattr(mounted_app, 'follow_symlink', False)),
                    'authorization_verified': False,
                }
        records.append(record)
    records.sort(key=lambda item: (item['path'], item['route_type'], item['name']))
    return {
        'non_api_route_count': len(records),
        'static_mount_count': sum('static_files' in item for item in records),
        'routes': records,
        'authorization_claim': False,
    }

def build_manifest(api_routes: Iterable[Any], app: Any = None, app_routes: Iterable[Any] | None = None) -> dict[str, Any]:
    api_routes = list(api_routes)
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
    counts = Counter(item["route_id"] for item in records)
    duplicate_ids = sorted(route_id for route_id, count in counts.items() if count > 1)
    if app_routes is None:
        app_routes = getattr(app, "routes", []) if app is not None else []
    non_api_surface = non_api_route_inventory(app_routes, api_routes)
    return {
        "schema_version": 3,
        "source": "FastAPI app.routes: APIRoute entries plus non-APIRoute Starlette routes/mounts",
        "authorization_claim": False,
        "note": (
            "Inventory only. Dependency presence does not prove authorization. "
            "UNCLASSIFIED means no approved policy is recorded; DENY_BY_DEFAULT "
            "is the required target policy, not proof that runtime currently denies access."
        ),
        "application_security_surface": application_security_surface(app) if app is not None else {
            "global_dependency_count": 0,
            "global_dependencies": [],
            "middleware_count": 0,
            "middleware": [],
            "authorization_claim": False,
            "source": "not supplied to build_manifest",
        },
        "non_api_http_surface": non_api_surface,
        "route_count": len(records),
        "duplicate_route_ids": duplicate_ids,
        "routes": records,
    }


def render_markdown(manifest: dict[str, Any]) -> str:
    routes = manifest["routes"]
    dependency_count = sum(
        len(item["dependencies"].get("dependencies", [])) for item in routes
    )
    surface = manifest.get("application_security_surface", {})
    non_api = manifest.get("non_api_http_surface", {})
    lines = [
        "# Studio FastAPI runtime route manifest",
        "",
        "> Generated from the imported FastAPI application. This is an inventory, not proof of access control.",
        "",
        f"- Registered APIRoute method/path entries: **{manifest['route_count']}**",
        f"- Additional non-APIRoute HTTP entries: **{non_api.get('non_api_route_count', 0)}**",
        f"- StaticFiles mounts: **{non_api.get('static_mount_count', 0)}**",
        f"- Top-level route dependency edges: **{dependency_count}**",
        f"- Duplicate method/path IDs: **{len(manifest['duplicate_route_ids'])}**",
        "- Policy status: **UNCLASSIFIED for every route**",
        "- Required target: **DENY_BY_DEFAULT until an explicit server-side policy is reviewed**",
        "",
        "## Application-wide dependencies and middleware",
        "",
        f"- Global FastAPI dependencies: **{surface.get('global_dependency_count', 0)}**",
        f"- Registered middleware: **{surface.get('middleware_count', 0)}**",
    ]
    for dependency in surface.get("global_dependencies", []):
        scopes = ", ".join(dependency.get("security_scopes", [])) or "none"
        lines.append(f"- Global dependency: `{dependency['call']}` (scopes: {scopes})")
    for middleware in surface.get("middleware", []):
        details = ""
        if "cors_options" in middleware:
            details = " — CORS " + json.dumps(middleware["cors_options"], ensure_ascii=False, sort_keys=True)
        lines.append(f"- Middleware: `{middleware['middleware']}`{details}")
    if surface.get("source") == "not supplied to build_manifest":
        lines.append("- Application object was not supplied; global surface was not inspected.")
    lines.extend(["", "## Non-APIRoute HTTP surface", ""])
    if not non_api.get("routes"):
        lines.append("- No non-APIRoute entries were supplied to the exporter.")
    else:
        lines.extend([
            "| Type | Path | Name | Methods | Mounted application / static configuration |",
            "|---|---|---|---|---|",
        ])
        for item in non_api["routes"]:
            details = item.get("mounted_app", "")
            if "static_files" in item:
                details += " " + json.dumps(item["static_files"], ensure_ascii=False, sort_keys=True)
            values = [item["route_type"], item["path"], item["name"], ", ".join(item["methods"]) or "—", details or "—"]
            lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\\n", " ") for value in values) + " |")

    lines.extend([
        "",
        "## API routes",
        "",
        "| Method | Path | Endpoint | Operation ID | Direct dependencies | Policy |",
        "|---|---|---|---|---:|---|",
    ])
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
        "- Middleware names and configuration are inventory evidence, not proof that a request is authenticated or authorized.",
        "- StaticFiles mounts are HTTP surfaces; filesystem paths are intentionally omitted from this artifact.",
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
    manifest = build_manifest(api_routes, app=app, app_routes=app.routes)
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
    print(
        f"Exported {manifest['route_count']} APIRoute method/path entries, "
        f"{manifest['non_api_http_surface']['non_api_route_count']} non-APIRoute entries, "
        f"{manifest['non_api_http_surface']['static_mount_count']} StaticFiles mounts."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
