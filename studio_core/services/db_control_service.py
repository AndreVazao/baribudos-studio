from __future__ import annotations

import socket
from typing import Any, Dict
from urllib.parse import urlparse

from studio_core.services.credential_resolver_service import resolve_credential


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _database_url() -> str:
    return resolve_credential(
        "BARIBUDOS_WEBSITE_DATABASE_URL",
        target="supabase",
        aliases=["DATABASE_URL"],
    )


def _supabase_url() -> str:
    return resolve_credential("BARIBUDOS_SUPABASE_URL", target="supabase")


def _supabase_service_key() -> str:
    return resolve_credential("BARIBUDOS_SUPABASE_SERVICE_ROLE_KEY", target="supabase")


def _extract_host_port() -> Dict[str, Any]:
    db_url = _database_url()
    if not db_url:
        return {"host": "", "port": None, "scheme": "", "database": ""}

    parsed = urlparse(db_url)
    database_name = (parsed.path or "").lstrip("/")
    return {
        "host": parsed.hostname or "",
        "port": parsed.port or 5432,
        "scheme": parsed.scheme or "",
        "database": database_name,
    }


def _probe_socket(host: str, port: int, timeout: float = 2.5) -> Dict[str, Any]:
    if not host or not port:
        return {"ok": False, "error": "host_or_port_missing"}

    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def get_db_control_status() -> Dict[str, Any]:
    db_url = _database_url()
    supabase_url = _supabase_url()
    supabase_key = _supabase_service_key()
    target = _extract_host_port()
    socket_probe = _probe_socket(target.get("host", ""), int(target.get("port") or 0)) if db_url else {"ok": False, "error": "database_url_missing"}

    return {
        "ok": True,
        "mode": "local_studio_control_plane",
        "database_configured": bool(db_url),
        "supabase_configured": bool(supabase_url),
        "supabase_service_role_configured": bool(supabase_key),
        "database_target": {
            "scheme": target.get("scheme", ""),
            "host": target.get("host", ""),
            "port": target.get("port"),
            "database": target.get("database", ""),
        },
        "network_probe": socket_probe,
        "notes": [
            "O Studio permanece local e soberano.",
            "Este módulo valida readiness e conectividade da base pública do Website sem expor segredos no frontend.",
            "Operações mutáveis devem continuar a entrar de forma faseada e segura.",
        ],
    }


def get_db_control_readiness() -> Dict[str, Any]:
    status = get_db_control_status()

    checklist = [
        {"field": "BARIBUDOS_WEBSITE_DATABASE_URL or DATABASE_URL", "ok": bool(status.get("database_configured"))},
        {"field": "BARIBUDOS_SUPABASE_URL", "ok": bool(status.get("supabase_configured"))},
        {"field": "BARIBUDOS_SUPABASE_SERVICE_ROLE_KEY", "ok": bool(status.get("supabase_service_role_configured"))},
        {"field": "database socket reachability", "ok": bool((status.get("network_probe") or {}).get("ok"))},
    ]

    ready = all(item["ok"] for item in checklist)

    return {
        "ok": True,
        "ready": ready,
        "checklist": checklist,
        "status": status,
    }
