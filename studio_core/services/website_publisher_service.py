from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List
from urllib import error, request

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, update_json_item
from studio_core.services.credential_resolver_service import resolve_credential
from studio_core.services.publication_policy_service import evaluate_project_publication_policy
from studio_core.services.website_control_service import (
    revalidate_website_publication,
    unpublish_website_publication,
)
from studio_core.services.website_contract_payload_service import build_website_payload_from_package

PROJECTS_FILE = "data/projects.json"
DEFAULT_SCHEMA_VERSION = "website_ingest_v1"
MAX_HISTORY_ITEMS = 50


def _load_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    if not isinstance(projects, list):
        return None
    for project in projects:
        if str(project.get("id", "")) == str(project_id):
            return project
    return None


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _to_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return fallback


def _get_project_public_state(project: Dict[str, Any]) -> str:
    commercial = _safe_dict(project.get("commercial"))
    marketing = _safe_dict(commercial.get("website_marketing") or commercial.get("marketing"))
    return _normalize_text(marketing.get("public_state")) or "private"


def _derive_website_manual_status(project: Dict[str, Any], fallback: str = "draft") -> str:
    public_state = _get_project_public_state(project)
    ready_for_publish = bool(project.get("ready_for_publish"))

    if public_state == "published":
        return "published"
    if public_state in {"prelaunch_public", "teaser_ready", "launch_ready"}:
        return "ready"
    if ready_for_publish:
        return "queued"
    return fallback


def _default_website_channel_state() -> Dict[str, Any]:
    return {
        "enabled": True,
        "manual_status": "",
        "attempts": 0,
        "last_attempt": "",
        "last_success_at": "",
        "last_error": "",
        "notes": "",
    }


def _normalize_distribution_hub(project: Dict[str, Any]) -> Dict[str, Any]:
    commercial = _safe_dict(project.get("commercial"))
    hub = _safe_dict(commercial.get("distribution_hub"))
    channels = _safe_dict(hub.get("channels"))

    return {
        "version": _normalize_text(hub.get("version")) or "v6",
        "project_id": _normalize_text(hub.get("project_id")) or _normalize_text(project.get("id")),
        "primary_channel": _normalize_text(hub.get("primary_channel")) or "website",
        "notes": _normalize_text(hub.get("notes")),
        "channels": {
            "website": {
                **_default_website_channel_state(),
                **_safe_dict(channels.get("website")),
            },
            "amazon": {
                **_default_website_channel_state(),
                **_safe_dict(channels.get("amazon")),
            },
            "youtube": {
                **_default_website_channel_state(),
                **_safe_dict(channels.get("youtube")),
            },
            "audio": {
                **_default_website_channel_state(),
                **_safe_dict(channels.get("audio")),
            },
        },
        "history": _safe_list(hub.get("history")),
        "created_at": _normalize_text(hub.get("created_at")) or now_iso(),
        "updated_at": _normalize_text(hub.get("updated_at")),
        "last_snapshot_at": _normalize_text(hub.get("last_snapshot_at")),
    }


def _build_history_entry(
    *,
    operation: str,
    status: str,
    project_id: str,
    note: str = "",
    publication_id: str = "",
    variant_id: str = "",
    checksum: str = "",
    error_message: str = "",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "at": now_iso(),
        "channel": "website",
        "operation": _normalize_text(operation),
        "status": _normalize_text(status),
        "project_id": _normalize_text(project_id),
        "publication_id": _normalize_text(publication_id),
        "variant_id": _normalize_text(variant_id),
        "checksum": _normalize_text(checksum),
        "note": _normalize_text(note),
        "error": _normalize_text(error_message),
        "payload": _safe_dict(payload),
    }


def _write_website_operational_state(
    project_id: str,
    *,
    manual_status: str | None = None,
    note: str = "",
    increment_attempt: bool = False,
    clear_error: bool = False,
    error_message: str | None = None,
    set_last_attempt: bool = False,
    set_last_success: bool = False,
    sync_patch: Dict[str, Any] | None = None,
    history_entry: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    def updater(current: Dict[str, Any]) -> Dict[str, Any]:
        commercial = _safe_dict(current.get("commercial"))
        hub = _normalize_distribution_hub(current)
        website_state = {
            **_default_website_channel_state(),
            **_safe_dict(_safe_dict(hub.get("channels")).get("website")),
        }

        timestamp = now_iso()

        if increment_attempt:
            website_state["attempts"] = _to_int(website_state.get("attempts"), 0) + 1
        if set_last_attempt:
            website_state["last_attempt"] = timestamp
        if set_last_success:
            website_state["last_success_at"] = timestamp
        if clear_error:
            website_state["last_error"] = ""
        if error_message is not None:
            website_state["last_error"] = _normalize_text(error_message)
        if manual_status is not None:
            website_state["manual_status"] = _normalize_text(manual_status)
        if note:
            website_state["notes"] = _normalize_text(note)

        history = _safe_list(hub.get("history"))
        if history_entry:
            history = [history_entry, *history][:MAX_HISTORY_ITEMS]

        next_hub = {
            **hub,
            "version": "v6",
            "project_id": _normalize_text(current.get("id")) or project_id,
            "primary_channel": _normalize_text(hub.get("primary_channel")) or "website",
            "channels": {
                **_safe_dict(hub.get("channels")),
                "website": website_state,
            },
            "history": history,
            "updated_at": timestamp,
            "last_snapshot_at": timestamp,
            "created_at": _normalize_text(hub.get("created_at")) or timestamp,
        }

        next_project = {
            **current,
            "commercial": {
                **commercial,
                "distribution_hub": next_hub,
            },
            "updated_at": timestamp,
        }

        if sync_patch is not None:
            next_project["website_sync"] = {
                **_safe_dict(current.get("website_sync")),
                **sync_patch,
            }

        return next_project

    return update_json_item(PROJECTS_FILE, project_id, updater)


def build_publish_envelope(project_id: str) -> Dict[str, Any]:
    project = _load_project(project_id)
    if not project:
        raise ValueError("project_not_found")

    policy = evaluate_project_publication_policy(project)
    if not bool(policy.get("eligible_for_website_publish", False)):
        raise ValueError(f"project_not_publishable:{','.join(policy.get('reasons', []))}")

    package = _safe_dict(project.get("publication_package"))
    frozen_at = _normalize_text(project.get("publication_package_frozen_at"))
    if not package:
        raise ValueError("publication_package_not_frozen")
    if not frozen_at:
        raise ValueError("publication_package_missing_freeze_timestamp")

    website_payload = build_website_payload_from_package(package)
    base_variant_id = _normalize_text(website_payload.get("project_id"))
    language = _normalize_text(website_payload.get("language")) or "pt-PT"
    final_variant_id = _normalize_text(website_payload.get("variant_id")) or f"{base_variant_id}:website:{language}:default"
    publication_id = f"{base_variant_id}:website"

    envelope = {
        "schema_version": DEFAULT_SCHEMA_VERSION,
        "publication_id": publication_id,
        "variant_id": final_variant_id,
        "project_id": _normalize_text(project.get("id")),
        "project_version": frozen_at,
        "published_at": now_iso(),
        "payload": website_payload,
        "related_variants": [],
        "related_projects": [],
        "asset_manifest": _safe_dict(_safe_dict(package.get("assets")).get("public")),
        "branding_pack": _safe_dict(_safe_dict(package.get("assets")).get("branding_resolution")),
        "marketplace_visuals": {
            "website": {
                "hero_background": _safe_dict(website_payload.get("assets")).get("hero_background", ""),
                "promo_banners": _safe_dict(website_payload.get("assets")).get("promo_banners", []),
                "social_cards": _safe_dict(website_payload.get("assets")).get("social_cards", []),
                "campaign_visuals": _safe_dict(website_payload.get("assets")).get("campaign_visuals", []),
            }
        },
    }

    envelope_bytes = json.dumps(envelope, ensure_ascii=False, sort_keys=True).encode("utf-8")
    envelope["checksum"] = hashlib.sha256(envelope_bytes).hexdigest()
    return envelope


def publish_project_to_website(project_id: str) -> Dict[str, Any]:
    project = _load_project(project_id)
    if not project:
        raise ValueError("project_not_found")

    target_url = resolve_credential("BARIBUDOS_WEBSITE_PUBLISH_URL", target="website")
    api_key = resolve_credential("BARIBUDOS_WEBSITE_PUBLISH_API_KEY", target="website")

    if not target_url:
        message = "website_publish_url_missing"
        _write_website_operational_state(
            project_id,
            manual_status="failed",
            note="Configuração do endpoint Website em falta.",
            error_message=message,
            history_entry=_build_history_entry(operation="publish", status="failed", project_id=project_id, note="Configuração do endpoint Website em falta.", error_message=message),
        )
        raise ValueError(message)
    if not api_key:
        message = "website_publish_api_key_missing"
        _write_website_operational_state(
            project_id,
            manual_status="failed",
            note="API key do Website em falta.",
            error_message=message,
            history_entry=_build_history_entry(operation="publish", status="failed", project_id=project_id, note="API key do Website em falta.", error_message=message),
        )
        raise ValueError(message)

    try:
        envelope = build_publish_envelope(project_id)
    except ValueError as exc:
        message = str(exc)
        _write_website_operational_state(
            project_id,
            manual_status="failed",
            note="Falha ao preparar envelope de publicação.",
            error_message=message,
            history_entry=_build_history_entry(operation="publish", status="failed", project_id=project_id, note="Falha ao preparar envelope de publicação.", error_message=message),
        )
        raise

    _write_website_operational_state(
        project_id,
        manual_status="queued",
        note="Publicação para Website iniciada pelo Studio.",
        increment_attempt=True,
        clear_error=True,
        set_last_attempt=True,
        history_entry=_build_history_entry(
            operation="publish",
            status="queued",
            project_id=project_id,
            note="Publicação para Website iniciada pelo Studio.",
            publication_id=_normalize_text(envelope.get("publication_id")),
            variant_id=_normalize_text(envelope.get("variant_id")),
            checksum=_normalize_text(envelope.get("checksum")),
            payload={
                "schema_version": envelope.get("schema_version"),
                "project_version": envelope.get("project_version"),
            },
        ),
    )

    body = json.dumps(envelope, ensure_ascii=False).encode("utf-8")

    http_request = request.Request(
        target_url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-studio-api-key": api_key,
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw) if raw else {"ok": True}
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        message = f"website_publish_http_error:{exc.code}:{details}"
        _write_website_operational_state(
            project_id,
            manual_status="failed",
            note="Publicação no Website falhou com erro HTTP.",
            error_message=message,
            history_entry=_build_history_entry(
                operation="publish",
                status="failed",
                project_id=project_id,
                note="Publicação no Website falhou com erro HTTP.",
                publication_id=_normalize_text(envelope.get("publication_id")),
                variant_id=_normalize_text(envelope.get("variant_id")),
                checksum=_normalize_text(envelope.get("checksum")),
                error_message=message,
            ),
        )
        raise ValueError(message) from exc
    except error.URLError as exc:
        message = f"website_publish_connection_error:{exc.reason}"
        _write_website_operational_state(
            project_id,
            manual_status="failed",
            note="Publicação no Website falhou por erro de ligação.",
            error_message=message,
            history_entry=_build_history_entry(
                operation="publish",
                status="failed",
                project_id=project_id,
                note="Publicação no Website falhou por erro de ligação.",
                publication_id=_normalize_text(envelope.get("publication_id")),
                variant_id=_normalize_text(envelope.get("variant_id")),
                checksum=_normalize_text(envelope.get("checksum")),
                error_message=message,
            ),
        )
        raise ValueError(message) from exc

    receipt = {
        "ok": bool(result.get("ok", False)),
        "target_url": target_url,
        "schema_version": envelope.get("schema_version"),
        "publication_id": envelope.get("publication_id"),
        "variant_id": envelope.get("variant_id"),
        "checksum": envelope.get("checksum"),
        "published_at": envelope.get("published_at"),
        "response": result,
        "synced_at": now_iso(),
    }

    updated_project = _write_website_operational_state(
        project_id,
        manual_status=_derive_website_manual_status(project, fallback="ready"),
        note="Website sincronizado com sucesso pelo Studio.",
        clear_error=True,
        set_last_success=True,
        sync_patch=receipt,
        history_entry=_build_history_entry(
            operation="publish",
            status="success",
            project_id=project_id,
            note="Website sincronizado com sucesso pelo Studio.",
            publication_id=_normalize_text(envelope.get("publication_id")),
            variant_id=_normalize_text(envelope.get("variant_id")),
            checksum=_normalize_text(envelope.get("checksum")),
            payload={
                "target_url": target_url,
                "response_ok": bool(result.get("ok", False)),
            },
        ),
    )

    return {
        "ok": True,
        "project_id": project_id,
        "envelope": envelope,
        "receipt": _safe_dict(updated_project.get("website_sync")),
    }


def unpublish_project_on_website(project_id: str) -> Dict[str, Any]:
    project = _load_project(project_id)
    if not project:
        raise ValueError("project_not_found")

    website_sync = _safe_dict(project.get("website_sync"))
    publication_id = _normalize_text(website_sync.get("publication_id"))
    if not publication_id:
        message = "website_publication_id_missing"
        _write_website_operational_state(
            project_id,
            manual_status="failed",
            note="Não existe publication_id para unpublish.",
            error_message=message,
            history_entry=_build_history_entry(operation="unpublish", status="failed", project_id=project_id, note="Não existe publication_id para unpublish.", error_message=message),
        )
        raise ValueError(message)

    _write_website_operational_state(
        project_id,
        manual_status="queued",
        note="Pedido de unpublish enviado ao Website.",
        increment_attempt=True,
        clear_error=True,
        set_last_attempt=True,
        history_entry=_build_history_entry(
            operation="unpublish",
            status="queued",
            project_id=project_id,
            note="Pedido de unpublish enviado ao Website.",
            publication_id=publication_id,
        ),
    )

    try:
        result = unpublish_website_publication(publication_id)
    except ValueError as exc:
        message = str(exc)
        _write_website_operational_state(
            project_id,
            manual_status="failed",
            note="Unpublish no Website falhou.",
            error_message=message,
            history_entry=_build_history_entry(operation="unpublish", status="failed", project_id=project_id, note="Unpublish no Website falhou.", publication_id=publication_id, error_message=message),
        )
        raise

    receipt = {
        **website_sync,
        "unpublished_at": now_iso(),
        "last_unpublish_result": result,
    }

    _write_website_operational_state(
        project_id,
        manual_status="draft",
        note="Conteúdo removido da superfície pública do Website.",
        clear_error=True,
        set_last_success=True,
        sync_patch=receipt,
        history_entry=_build_history_entry(
            operation="unpublish",
            status="success",
            project_id=project_id,
            note="Conteúdo removido da superfície pública do Website.",
            publication_id=publication_id,
            payload={"result": result if isinstance(result, dict) else {"value": str(result)}},
        ),
    )

    return {"ok": True, "project_id": project_id, "publication_id": publication_id, "result": result}


def revalidate_project_on_website(project_id: str) -> Dict[str, Any]:
    project = _load_project(project_id)
    if not project:
        raise ValueError("project_not_found")

    website_sync = _safe_dict(project.get("website_sync"))
    publication_id = _normalize_text(website_sync.get("publication_id"))
    if not publication_id:
        message = "website_publication_id_missing"
        _write_website_operational_state(
            project_id,
            manual_status="failed",
            note="Não existe publication_id para revalidate.",
            error_message=message,
            history_entry=_build_history_entry(operation="revalidate", status="failed", project_id=project_id, note="Não existe publication_id para revalidate.", error_message=message),
        )
        raise ValueError(message)

    _write_website_operational_state(
        project_id,
        manual_status="queued",
        note="Pedido de revalidate enviado ao Website.",
        increment_attempt=True,
        clear_error=True,
        set_last_attempt=True,
        history_entry=_build_history_entry(
            operation="revalidate",
            status="queued",
            project_id=project_id,
            note="Pedido de revalidate enviado ao Website.",
            publication_id=publication_id,
        ),
    )

    try:
        result = revalidate_website_publication(publication_id)
    except ValueError as exc:
        message = str(exc)
        _write_website_operational_state(
            project_id,
            manual_status="failed",
            note="Revalidate no Website falhou.",
            error_message=message,
            history_entry=_build_history_entry(operation="revalidate", status="failed", project_id=project_id, note="Revalidate no Website falhou.", publication_id=publication_id, error_message=message),
        )
        raise

    receipt = {
        **website_sync,
        "last_revalidate_at": now_iso(),
        "last_revalidate_result": result,
    }

    _write_website_operational_state(
        project_id,
        manual_status=_derive_website_manual_status(project, fallback="ready"),
        note="Website revalidado com sucesso.",
        clear_error=True,
        set_last_success=True,
        sync_patch=receipt,
        history_entry=_build_history_entry(
            operation="revalidate",
            status="success",
            project_id=project_id,
            note="Website revalidado com sucesso.",
            publication_id=publication_id,
            payload={"result": result if isinstance(result, dict) else {"value": str(result)}},
        ),
    )

    return {"ok": True, "project_id": project_id, "publication_id": publication_id, "result": result}


def get_project_publish_status(project_id: str) -> Dict[str, Any]:
    project = _load_project(project_id)
    if not project:
        raise ValueError("project_not_found")

    package = _safe_dict(project.get("publication_package"))
    website_sync = _safe_dict(project.get("website_sync"))
    policy = evaluate_project_publication_policy(project)

    return {
        "ok": True,
        "project_id": project_id,
        "has_frozen_package": bool(package),
        "publication_package_frozen_at": project.get("publication_package_frozen_at", ""),
        "website_sync": website_sync,
        "publication_policy": policy,
    }
