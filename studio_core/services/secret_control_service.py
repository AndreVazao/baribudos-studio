from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import append_json_item, list_json_items, read_json, remove_json_item, update_json_item

SECRETS_VAULTS_FILE = "data/secret_vaults.json"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _mask_value(value: str) -> str:
    text = _normalize_text(value)
    if not text:
        return ""
    if len(text) <= 4:
        return "*" * len(text)
    return f"{text[:2]}{'*' * max(4, len(text) - 4)}{text[-2:]}"


def _parse_env_text(raw_text: str) -> List[Dict[str, Any]]:
    lines = str(raw_text or "").splitlines()
    rows: List[Dict[str, Any]] = []

    for index, raw in enumerate(lines):
        original = raw.rstrip("\n")
        stripped = original.strip()

        if not stripped:
            rows.append({
                "id": str(uuid4()),
                "kind": "blank",
                "raw": original,
                "position": index,
            })
            continue

        if stripped.startswith("#"):
            rows.append({
                "id": str(uuid4()),
                "kind": "comment",
                "raw": original,
                "position": index,
            })
            continue

        working = stripped
        has_export = False
        if working.startswith("export "):
            has_export = True
            working = working[7:].strip()

        if "=" not in working:
            rows.append({
                "id": str(uuid4()),
                "kind": "raw",
                "raw": original,
                "position": index,
            })
            continue

        key, value = working.split("=", 1)
        key = key.strip()
        value = value.strip()
        quote_style = "none"

        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            quote_style = "double"
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'") and len(value) >= 2:
            quote_style = "single"
            value = value[1:-1]
        else:
            if " #" in value:
                value = value.split(" #", 1)[0].rstrip()

        rows.append({
            "id": str(uuid4()),
            "kind": "entry",
            "key": key,
            "value": value,
            "masked_value": _mask_value(value),
            "quote_style": quote_style,
            "has_export": has_export,
            "raw": original,
            "position": index,
        })

    return rows


def _serialize_rows(rows: List[Dict[str, Any]]) -> str:
    output: List[str] = []

    for row in rows:
        kind = row.get("kind")
        if kind == "blank":
            output.append("")
            continue
        if kind in {"comment", "raw"}:
            output.append(_normalize_text(row.get("raw")))
            continue

        key = _normalize_text(row.get("key"))
        value = str(row.get("value") or "")
        quote_style = _normalize_text(row.get("quote_style")) or "none"
        has_export = bool(row.get("has_export", False))

        if quote_style == "double":
            rendered = f'"{value}"'
        elif quote_style == "single":
            rendered = f"'{value}'"
        else:
            rendered = value

        prefix = "export " if has_export else ""
        output.append(f"{prefix}{key}={rendered}")

    return "\n".join(output)


def _build_vault_response(vault: Dict[str, Any], include_values: bool = False) -> Dict[str, Any]:
    rows = []
    for row in list(vault.get("rows") or []):
        if row.get("kind") != "entry":
            rows.append(row)
            continue
        row_copy = dict(row)
        if not include_values:
            row_copy["value"] = ""
        row_copy["masked_value"] = _mask_value(str(row.get("value") or ""))
        rows.append(row_copy)

    return {
        **vault,
        "rows": rows,
        "rendered_env": _serialize_rows(list(vault.get("rows") or [])),
    }


def list_secret_vaults() -> Dict[str, Any]:
    vaults = list_json_items(SECRETS_VAULTS_FILE)
    return {
        "ok": True,
        "vaults": [_build_vault_response(vault, include_values=False) for vault in vaults],
        "count": len(vaults),
    }


def get_secret_vault(vault_id: str, reveal_values: bool = False) -> Dict[str, Any]:
    vaults = list_json_items(SECRETS_VAULTS_FILE)
    for vault in vaults:
        if str(vault.get("id", "")) == str(vault_id):
            return _build_vault_response(vault, include_values=reveal_values)
    raise ValueError("vault_not_found")


def create_secret_vault(payload: Dict[str, Any]) -> Dict[str, Any]:
    name = _normalize_text(payload.get("name"))
    if not name:
        raise ValueError("vault_name_missing")

    raw_text = str(payload.get("raw_text") or "")
    rows = _parse_env_text(raw_text)

    vault = {
        "id": str(uuid4()),
        "name": name,
        "target": _normalize_text(payload.get("target")) or "custom",
        "environment": _normalize_text(payload.get("environment")) or "local",
        "file_name": _normalize_text(payload.get("file_name")) or ".env",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "rows": rows,
        "source_of_truth": "studio",
        "notes": _normalize_text(payload.get("notes")),
    }
    append_json_item(SECRETS_VAULTS_FILE, vault)
    return _build_vault_response(vault, include_values=False)


def update_secret_vault(vault_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    def _updater(current: Dict[str, Any]) -> Dict[str, Any]:
        rows = list(current.get("rows") or [])
        if "raw_text" in payload:
            rows = _parse_env_text(str(payload.get("raw_text") or ""))
        if "rows" in payload and isinstance(payload.get("rows"), list):
            rows = list(payload.get("rows") or [])

        return {
            **current,
            "name": _normalize_text(payload.get("name")) or current.get("name", ""),
            "target": _normalize_text(payload.get("target")) or current.get("target", "custom"),
            "environment": _normalize_text(payload.get("environment")) or current.get("environment", "local"),
            "file_name": _normalize_text(payload.get("file_name")) or current.get("file_name", ".env"),
            "notes": _normalize_text(payload.get("notes")) if "notes" in payload else current.get("notes", ""),
            "rows": rows,
            "updated_at": now_iso(),
        }

    updated = update_json_item(SECRETS_VAULTS_FILE, vault_id, _updater)
    return _build_vault_response(updated, include_values=False)


def delete_secret_vault(vault_id: str) -> Dict[str, Any]:
    return remove_json_item(SECRETS_VAULTS_FILE, vault_id)


def export_secret_vault(vault_id: str) -> Dict[str, Any]:
    vaults = list_json_items(SECRETS_VAULTS_FILE)
    for vault in vaults:
        if str(vault.get("id", "")) == str(vault_id):
            return {
                "ok": True,
                "vault_id": vault_id,
                "file_name": vault.get("file_name") or ".env",
                "content": _serialize_rows(list(vault.get("rows") or [])),
            }
    raise ValueError("vault_not_found")
