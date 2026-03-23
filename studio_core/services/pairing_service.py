from __future__ import annotations

import json
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from studio_core.core.config import resolve_storage_path


PAIRING_PATH = resolve_storage_path("pairing/pairing_registry.json")
PAIRING_EXPIRY_HOURS = 72


def _now() -> datetime:
    return datetime.utcnow()


def _now_iso() -> str:
    return _now().isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _load_registry() -> List[Dict[str, Any]]:
    if not PAIRING_PATH.exists():
        return []
    try:
        return _safe_list(json.loads(PAIRING_PATH.read_text(encoding="utf-8")))
    except Exception:
        return []


def _save_registry(items: List[Dict[str, Any]]) -> None:
    PAIRING_PATH.parent.mkdir(parents=True, exist_ok=True)
    PAIRING_PATH.write_text(
        json.dumps(items, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _generate_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    parts = []
    for _ in range(3):
        parts.append("".join(secrets.choice(alphabet) for _ in range(4)))
    return f"BARI-{parts[0]}-{parts[1]}-{parts[2]}"


def _is_expired(item: Dict[str, Any]) -> bool:
    expires_at = _safe_str(item.get("expires_at"))
    if not expires_at:
        return False

    try:
        expiry = datetime.fromisoformat(expires_at)
        return _now() > expiry
    except Exception:
        return False


def _cleanup_expired(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [item for item in items if not _is_expired(item)]


def list_pairings() -> Dict[str, Any]:
    items = _cleanup_expired(_load_registry())
    _save_registry(items)

    return {
        "ok": True,
        "count": len(items),
        "items": items,
    }


def create_pairing(
    *,
    pc_name: str,
    lan_host: str,
    remote_host: str = "",
    created_by: str = "",
) -> Dict[str, Any]:
    items = _cleanup_expired(_load_registry())

    code = _generate_code()
    existing_codes = {str(item.get("pair_code")) for item in items}

    while code in existing_codes:
      code = _generate_code()

    expires_at = (_now() + timedelta(hours=PAIRING_EXPIRY_HOURS)).isoformat()

    record = {
        "pair_code": code,
        "pc_name": _safe_str(pc_name),
        "lan_host": _safe_str(lan_host),
        "remote_host": _safe_str(remote_host),
        "created_by": _safe_str(created_by),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "expires_at": expires_at,
        "is_active": True,
    }

    items.append(record)
    _save_registry(items)

    return {
        "ok": True,
        "pairing": record,
    }


def get_pairing_by_code(pair_code: str) -> Optional[Dict[str, Any]]:
    normalized = _safe_str(pair_code).upper()
    if not normalized:
        return None

    items = _cleanup_expired(_load_registry())
    _save_registry(items)

    for item in items:
        if _safe_str(item.get("pair_code")).upper() == normalized and bool(item.get("is_active", True)):
            return item

    return None


def resolve_pairing(pair_code: str) -> Dict[str, Any]:
    item = get_pairing_by_code(pair_code)
    if not item:
        return {
            "ok": False,
            "error": "pair_code_not_found",
        }

    return {
        "ok": True,
        "pairing": {
            "pair_code": item.get("pair_code"),
            "pc_name": item.get("pc_name"),
            "lan_host": item.get("lan_host"),
            "remote_host": item.get("remote_host"),
        },
    }


def revoke_pairing(pair_code: str) -> Dict[str, Any]:
    normalized = _safe_str(pair_code).upper()
    items = _cleanup_expired(_load_registry())
    updated = None

    for item in items:
        if _safe_str(item.get("pair_code")).upper() != normalized:
            continue

        item["is_active"] = False
        item["updated_at"] = _now_iso()
        updated = item
        break

    _save_registry(items)

    if not updated:
        return {
            "ok": False,
            "error": "pair_code_not_found",
        }

    return {
        "ok": True,
        "pairing": updated,
}
