#!/usr/bin/env python3
"""Generate a heuristic inventory of FastAPI route authorization surfaces.

This is a review aid, not proof that a route is protected or unprotected.
Global middleware, imported dependencies and service-layer checks require
manual verification before changing authentication behaviour.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "api_route", "websocket"}
AUTH_NAME_MARKERS = (
    "auth", "authenticate", "authorize", "permission", "require_user",
    "require_admin", "require_owner", "current_user", "current_session",
    "verify_token", "assert_admin", "assert_owner", "principal",
)
IDENTITY_NAMES = {"user_name", "user_role", "user_id"}
SENSITIVE_PATH_MARKERS = (
    "user", "secret", "vault", "db_control", "deploy", "updater",
    "publish", "publishing", "commerce", "commercial", "website",
    "memory", "pairing", "settings", "project",
)
DANGEROUS_OPERATION_NAMES = {
    "Popen", "run", "system", "rmtree", "unlink", "remove",
    "write_text", "write_bytes", "open", "execute", "exec",
}


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def literal_string(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        return ast.unparse(node)
    return value if isinstance(value, str) else str(value)


def _auth_names(node: ast.AST) -> set[str]:
    found: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = dotted_name(child.func)
            leaf = name.rsplit(".", 1)[-1].lower()
            if any(marker in leaf for marker in AUTH_NAME_MARKERS):
                found.add(name)
        elif isinstance(child, ast.Name):
            leaf = child.id.lower()
            if any(marker in leaf for marker in AUTH_NAME_MARKERS):
                found.add(child.id)
        elif isinstance(child, ast.Constant) and isinstance(child.value, str):
            value = child.value.lower()
            if value in {"authorization", "x-api-key", "x-studio-api-key", "x-admin-key"}:
                found.add(f"header:{child.value}")
    return found


def _identity_inputs(node: ast.AST) -> set[str]:
    found: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id in IDENTITY_NAMES:
            found.add(child.id)
        elif isinstance(child, ast.arg) and child.arg in IDENTITY_NAMES:
            found.add(child.arg)
        elif isinstance(child, ast.Attribute) and child.attr in IDENTITY_NAMES:
            found.add(child.attr)
    return found


def _dangerous_operations(node: ast.AST) -> set[str]:
    found: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = dotted_name(child.func)
            leaf = name.rsplit(".", 1)[-1]
            if leaf in DANGEROUS_OPERATION_NAMES:
                found.add(name)
        elif isinstance(child, ast.Attribute):
            if child.attr in DANGEROUS_OPERATION_NAMES:
                found.add(child.attr)
    return found


def _module_auth_names(tree: ast.Module) -> set[str]:
    found: set[str] = set()
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not isinstance(value, ast.Call) or dotted_name(value.func).rsplit(".", 1)[-1] != "APIRouter":
            continue
        for keyword in value.keywords:
            if keyword.arg == "dependencies":
                found.update(_auth_names(keyword.value))
    return found


def scan_source(source: str, path: str) -> list[dict[str, Any]]:
    tree = ast.parse(source, filename=path)
    module_auth = _module_auth_names(tree)
    records: list[dict[str, Any]] = []
    path_lower = path.lower()
    sensitive_path = any(marker in path_lower for marker in SENSITIVE_PATH_MARKERS)

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            if not isinstance(decorator.func.value, ast.Name) or decorator.func.value.id != "router":
                continue
            method = decorator.func.attr.lower()
            if method not in ROUTE_METHODS:
                continue
            route_path = literal_string(decorator.args[0]) if decorator.args else ""
            evidence = _auth_names(node) | _auth_names(decorator) | module_auth
            identities = _identity_inputs(node)
            dangerous = _dangerous_operations(node)
            records.append({
                "module": path,
                "function": node.name,
                "line": node.lineno,
                "method": method.upper(),
                "path": route_path,
                "auth_signal": bool(evidence),
                "auth_evidence": sorted(evidence),
                "client_identity_inputs": sorted(identities),
                "sensitive_surface": sensitive_path or bool(identities) or bool(dangerous),
                "dangerous_operation_signals": sorted(dangerous),
            })
    return records


def scan_routes(routes_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(routes_dir.glob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
            records.extend(scan_source(source, path.as_posix()))
        except (OSError, SyntaxError) as exc:
            records.append({
                "module": path.as_posix(),
                "function": "<parse-error>",
                "line": 0,
                "method": "",
                "path": "",
                "auth_signal": False,
                "auth_evidence": [],
                "client_identity_inputs": [],
                "sensitive_surface": True,
                "dangerous_operation_signals": [f"parse-error:{type(exc).__name__}"],
            })
    return records


def render_markdown(records: list[dict[str, Any]], module_count: int) -> str:
    no_signal = sum(not item["auth_signal"] for item in records)
    identity = sum(bool(item["client_identity_inputs"]) for item in records)
    sensitive = sum(item["sensitive_surface"] for item in records)
    lines = [
        "# Studio API route authorization surface inventory",
        "",
        "> Heuristic static inventory only. An authorization signal is not proof of correct enforcement; absence of a signal is not proof of exposure. Verify global middleware, imported dependencies, service-layer checks and runtime behaviour manually.",
        "",
        f"- Route modules scanned: **{module_count}**",
        f"- Route handlers found: **{len(records)}**",
        f"- Handlers without a detected local auth signal: **{no_signal}**",
        f"- Handlers referencing client identity fields: **{identity}**",
        f"- Handlers flagged as sensitive or operational: **{sensitive}**",
        "",
        "| Method | Path | Handler | Auth signal | Client identity fields | Sensitive / operation signals |",
        "|---|---|---|---|---|---|",
    ]
    for item in records:
        handler = f"{item['module']}:{item['function']}:{item['line']}"
        auth = ", ".join(item["auth_evidence"]) if item["auth_evidence"] else "none detected"
        identity_fields = ", ".join(item["client_identity_inputs"]) or "—"
        signals = ", ".join(item["dangerous_operation_signals"]) or ("yes" if item["sensitive_surface"] else "—")
        values = [item["method"], item["path"], handler, auth, identity_fields, signals]
        lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    lines.extend([
        "",
        "## Required manual review",
        "",
        "1. Trace each handler through every service it calls; do not treat a local signal as sufficient authorization.",
        "2. Verify deny-by-default behaviour for anonymous, expired, revoked, disabled and insufficient-role sessions.",
        "3. Check router-level and application middleware dependencies that static per-handler analysis may not see.",
        "4. Replace authorization decisions based on client-supplied user identity or role with server-derived principals.",
        "5. Re-run this inventory whenever route modules change and attach the report to the security review.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--routes-dir", type=Path, default=Path(__file__).resolve().parents[1] / "studio_core" / "api" / "routes")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    records = scan_routes(args.routes_dir)
    module_count = len(list(args.routes_dir.glob("*.py")))
    markdown = render_markdown(records, module_count)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps({
            "module_count": module_count,
            "route_count": len(records),
            "heuristic_only": True,
            "routes": records,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
