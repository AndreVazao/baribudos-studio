from __future__ import annotations

from typing import Any, Dict, List

from studio_core.core.models import now_iso
from studio_core.core.storage import get_json_item, update_json_item

PROJECTS_FILE = "data/projects.json"

CHANNEL_LABELS = {
    "website": "Website próprio",
    "amazon": "Amazon KDP",
    "youtube": "YouTube / YouTube Kids",
    "audio": "Audiobook / outras plataformas",
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _to_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return fallback


DEFAULT_CHANNEL_STATE = {
    "enabled": True,
    "manual_status": "",
    "attempts": 0,
    "last_attempt": "",
    "last_success_at": "",
    "last_error": "",
    "notes": "",
}


DEFAULT_WEBSITE_MARKETING = {
    "public_state": "private",
    "teaser_badge": "Em breve",
    "teaser_headline": "",
    "teaser_subtitle": "",
    "teaser_cta_label": "Ver novidades",
    "teaser_release_label": "",
    "teaser_gallery": [],
    "teaser_cover_url": "",
    "teaser_trailer_url": "",
    "teaser_excerpt": "",
    "teaser_visibility_notes": "",
    "prelaunch_enabled": False,
    "share_preview_images_during_production": True,
}


def _normalize_channels(value: Any) -> Dict[str, Dict[str, Any]]:
    raw = value if isinstance(value, dict) else {}
    channels: Dict[str, Dict[str, Any]] = {}

    for channel_id in CHANNEL_LABELS.keys():
        item = raw.get(channel_id) if isinstance(raw.get(channel_id), dict) else {}
        channels[channel_id] = {
            "enabled": bool(item.get("enabled", True)),
            "manual_status": _text(item.get("manual_status")),
            "attempts": _to_int(item.get("attempts"), 0),
            "last_attempt": _text(item.get("last_attempt")),
            "last_success_at": _text(item.get("last_success_at")),
            "last_error": _text(item.get("last_error")),
            "notes": _text(item.get("notes")),
        }

    return channels


def _get_project(project_id: str) -> Dict[str, Any] | None:
    return get_json_item(PROJECTS_FILE, project_id)


def _get_marketing(project: Dict[str, Any]) -> Dict[str, Any]:
    commercial = _as_dict(project.get("commercial"))
    raw = commercial.get("website_marketing") or commercial.get("marketing") or {}
    marketing = DEFAULT_WEBSITE_MARKETING.copy()
    if isinstance(raw, dict):
        marketing.update(raw)
    marketing["teaser_gallery"] = _as_list(marketing.get("teaser_gallery"))
    return marketing


def _get_distribution_hub(project: Dict[str, Any]) -> Dict[str, Any]:
    commercial = _as_dict(project.get("commercial"))
    hub = _as_dict(commercial.get("distribution_hub"))
    return {
        "version": _text(hub.get("version")) or "v6",
        "project_id": _text(hub.get("project_id")) or _text(project.get("id")),
        "primary_channel": _text(hub.get("primary_channel")) or "website",
        "notes": _text(hub.get("notes")),
        "channels": _normalize_channels(hub.get("channels")),
        "history": _as_list(hub.get("history")),
        "created_at": _text(hub.get("created_at")),
        "updated_at": _text(hub.get("updated_at")),
        "last_snapshot_at": _text(hub.get("last_snapshot_at")),
    }


def _get_website_sync(project: Dict[str, Any]) -> Dict[str, Any]:
    return _as_dict(project.get("website_sync"))


def _get_status_meta(status: str) -> Dict[str, str]:
    current = _text(status).lower()
    if current == "published":
        return {"label": "published", "bg": "rgba(34,197,94,0.15)", "color": "#166534"}
    if current == "ready":
        return {"label": "ready", "bg": "rgba(59,130,246,0.15)", "color": "#1d4ed8"}
    if current == "queued":
        return {"label": "queued", "bg": "rgba(245,158,11,0.18)", "color": "#92400e"}
    if current == "failed":
        return {"label": "failed", "bg": "rgba(239,68,68,0.12)", "color": "#991b1b"}
    if current == "planned":
        return {"label": "planned", "bg": "rgba(148,163,184,0.18)", "color": "#475569"}
    return {"label": "draft", "bg": "rgba(100,116,139,0.12)", "color": "#475569"}


def _derive_channel_status(ready_signals: int, published_signals: bool, failed_signals: bool) -> str:
    if published_signals:
        return "published"
    if failed_signals:
        return "failed"
    if ready_signals >= 3:
        return "ready"
    if ready_signals >= 1:
        return "planned"
    return "draft"


def _build_sales_readiness(project: Dict[str, Any], marketing: Dict[str, Any], website_sync: Dict[str, Any]) -> Dict[str, Any]:
    checks = [
        {"key": "headline", "label": "Headline forte", "ok": bool(_text(marketing.get("teaser_headline")))},
        {"key": "subtitle", "label": "Subtítulo claro", "ok": bool(_text(marketing.get("teaser_subtitle")))},
        {"key": "cta", "label": "CTA definido", "ok": bool(_text(marketing.get("teaser_cta_label")))},
        {"key": "cover", "label": "Cover principal", "ok": bool(_text(marketing.get("teaser_cover_url")) or _text(project.get("cover_image")))},
        {"key": "gallery", "label": "Galeria mínima", "ok": len(_as_list(marketing.get("teaser_gallery"))) > 0},
        {
            "key": "state",
            "label": "Estado público coerente",
            "ok": _text(marketing.get("public_state")) in {"teaser_ready", "prelaunch_public", "launch_ready", "published"},
        },
        {"key": "project-ready", "label": "Projeto pronto para publicação", "ok": bool(project.get("ready_for_publish"))},
        {
            "key": "website-sync",
            "label": "Sync Website conhecido",
            "ok": bool(
                _text(website_sync.get("publication_id"))
                or _text(website_sync.get("published_at"))
                or _text(website_sync.get("last_revalidate_at"))
            ),
        },
    ]

    completed = len([item for item in checks if item["ok"]])
    total = len(checks)
    ratio = (completed / total) if total else 0

    label = "Ainda não deve avançar"
    color = "#991b1b"
    bg = "rgba(239,68,68,0.10)"

    if ratio >= 1:
        label = "Pronto para vender"
        color = "#166534"
        bg = "rgba(34,197,94,0.12)"
    elif ratio >= 0.75:
        label = "Quase pronto para vender"
        color = "#1d4ed8"
        bg = "rgba(59,130,246,0.12)"
    elif ratio >= 0.5:
        label = "Precisa de fechar mais base comercial"
        color = "#92400e"
        bg = "rgba(245,158,11,0.14)"

    return {
        "checks": checks,
        "completed": completed,
        "total": total,
        "ratio": ratio,
        "label": label,
        "color": color,
        "bg": bg,
    }


def _build_external_outputs(marketing: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "id": "website",
            "label": "Website próprio",
            "outputs": [
                {"label": "Teaser público", "ok": bool(_text(marketing.get("teaser_headline")))},
                {"label": "Caminho de compra", "ok": bool(_text(marketing.get("teaser_cta_label")))},
                {"label": "Cover comercial", "ok": bool(_text(marketing.get("teaser_cover_url")))},
            ],
        },
        {
            "id": "amazon",
            "label": "Amazon KDP",
            "outputs": [
                {"label": "Capa final", "ok": bool(_text(marketing.get("teaser_cover_url")))},
                {"label": "Copy comercial", "ok": bool(_text(marketing.get("teaser_subtitle")))},
                {"label": "Texto de lançamento", "ok": bool(_text(marketing.get("teaser_release_label")))},
            ],
        },
        {
            "id": "youtube",
            "label": "YouTube / YouTube Kids",
            "outputs": [
                {"label": "Vídeo principal", "ok": bool(_text(marketing.get("teaser_trailer_url")))},
                {"label": "Título forte", "ok": bool(_text(marketing.get("teaser_headline")))},
                {"label": "Descrição base", "ok": bool(_text(marketing.get("teaser_excerpt")) or _text(marketing.get("teaser_subtitle")))},
            ],
        },
        {
            "id": "audio",
            "label": "Audiobook / outras plataformas",
            "outputs": [
                {"label": "Copy base", "ok": bool(_text(marketing.get("teaser_excerpt")))},
                {"label": "Capa", "ok": bool(_text(marketing.get("teaser_cover_url")))},
                {"label": "Título de saída", "ok": bool(_text(marketing.get("teaser_headline")))},
            ],
        },
    ]


def _build_destinations(project: Dict[str, Any], marketing: Dict[str, Any], website_sync: Dict[str, Any], hub: Dict[str, Any]) -> List[Dict[str, Any]]:
    public_state = _text(marketing.get("public_state")) or "private"
    ready = bool(project.get("ready_for_publish"))
    channels = hub.get("channels") or {}
    has_website_activity = bool(
        _text(website_sync.get("published_at"))
        or _text(website_sync.get("last_revalidate_at"))
        or _text(website_sync.get("publication_id"))
    )

    website_computed_status = (
        "published"
        if public_state == "published"
        else "ready"
        if public_state in {"prelaunch_public", "teaser_ready", "launch_ready"}
        else "queued"
        if ready
        else "draft"
    )

    website_state = channels.get("website") or DEFAULT_CHANNEL_STATE.copy()
    website_status = _text(website_state.get("manual_status")) or website_computed_status

    destinations = [
        {
            "id": "website",
            "label": CHANNEL_LABELS["website"],
            "description": "Destino ativo agora. Recebe teaser, pré-lançamento, lançamento e revalidate.",
            "status": website_status,
            "status_meta": _get_status_meta(website_status),
            "enabled": bool(website_state.get("enabled", True)),
            "detail": (
                f"Sync conhecido: {_text(website_sync.get('published_at')) or _text(website_sync.get('last_revalidate_at')) or _text(website_sync.get('publication_id'))}"
                if has_website_activity
                else "Sem publicação conhecida ainda."
            ),
            "attempts": _to_int(website_state.get("attempts"), 0),
            "last_attempt": _text(website_state.get("last_attempt")) or "-",
            "last_success_at": _text(website_state.get("last_success_at")) or _text(website_sync.get("published_at")) or "-",
            "last_error": _text(website_state.get("last_error")) or ("-" if public_state == "private" else "Sem erro conhecido."),
            "notes": _text(website_state.get("notes")) or (
                "Canal próprio principal e primeiro motor de monetização."
                if public_state == "published"
                else "Usar este canal para validar descoberta e compra antes de escalar."
            ),
            "payload_snapshot": {
                "title": _text(marketing.get("teaser_headline")) or _text(project.get("title")) or "-",
                "cta": _text(marketing.get("teaser_cta_label")) or "-",
                "cover": _text(marketing.get("teaser_cover_url")) or "-",
            },
        },
        {
            "id": "amazon",
            "label": CHANNEL_LABELS["amazon"],
            "description": "Destino seguinte para ebooks e expansão editorial.",
            "status": _text((channels.get("amazon") or {}).get("manual_status")) or _derive_channel_status(
                ready_signals=len([
                    value for value in [
                        _text(marketing.get("teaser_cover_url")),
                        _text(marketing.get("teaser_subtitle")),
                        _text(marketing.get("teaser_release_label")),
                    ] if value
                ]),
                published_signals=False,
                failed_signals=False,
            ),
            "status_meta": _get_status_meta(_text((channels.get("amazon") or {}).get("manual_status")) or _derive_channel_status(
                ready_signals=len([
                    value for value in [
                        _text(marketing.get("teaser_cover_url")),
                        _text(marketing.get("teaser_subtitle")),
                        _text(marketing.get("teaser_release_label")),
                    ] if value
                ]),
                published_signals=False,
                failed_signals=False,
            )),
            "enabled": bool((channels.get("amazon") or {}).get("enabled", True)),
            "detail": "Pode ser o primeiro canal externo depois de validar receita no Website." if ready else "Ainda precisa de mais base editorial e comercial.",
            "attempts": _to_int((channels.get("amazon") or {}).get("attempts"), 0),
            "last_attempt": _text((channels.get("amazon") or {}).get("last_attempt")) or "-",
            "last_success_at": _text((channels.get("amazon") or {}).get("last_success_at")) or "-",
            "last_error": _text((channels.get("amazon") or {}).get("last_error")) or "-",
            "notes": _text((channels.get("amazon") or {}).get("notes")) or "Preparar capa, copy comercial, texto de lançamento e metadados finais.",
            "payload_snapshot": {
                "title": _text(marketing.get("teaser_headline")) or _text(project.get("title")) or "-",
                "commercial_copy": _text(marketing.get("teaser_subtitle")) or "-",
                "release_text": _text(marketing.get("teaser_release_label")) or "-",
            },
        },
        {
            "id": "youtube",
            "label": CHANNEL_LABELS["youtube"],
            "description": "Destino seguinte para trailers, séries e descoberta audiovisual.",
            "status": _text((channels.get("youtube") or {}).get("manual_status")) or _derive_channel_status(
                ready_signals=len([
                    value for value in [
                        _text(marketing.get("teaser_trailer_url")),
                        _text(marketing.get("teaser_headline")),
                        _text(marketing.get("teaser_excerpt")) or _text(marketing.get("teaser_subtitle")),
                    ] if value
                ]),
                published_signals=False,
                failed_signals=False,
            ),
            "status_meta": _get_status_meta(_text((channels.get("youtube") or {}).get("manual_status")) or _derive_channel_status(
                ready_signals=len([
                    value for value in [
                        _text(marketing.get("teaser_trailer_url")),
                        _text(marketing.get("teaser_headline")),
                        _text(marketing.get("teaser_excerpt")) or _text(marketing.get("teaser_subtitle")),
                    ] if value
                ]),
                published_signals=False,
                failed_signals=False,
            )),
            "enabled": bool((channels.get("youtube") or {}).get("enabled", True)),
            "detail": "Já existe base de vídeo para preparar uma saída externa." if _text(marketing.get("teaser_trailer_url")) else "Sem vídeo principal ainda, por isso ainda não é o melhor próximo passo.",
            "attempts": _to_int((channels.get("youtube") or {}).get("attempts"), 0),
            "last_attempt": _text((channels.get("youtube") or {}).get("last_attempt")) or "-",
            "last_success_at": _text((channels.get("youtube") or {}).get("last_success_at")) or "-",
            "last_error": _text((channels.get("youtube") or {}).get("last_error")) or "-",
            "notes": _text((channels.get("youtube") or {}).get("notes")) or "Preparar vídeo, título, descrição e eventual thumbnail por ativo.",
            "payload_snapshot": {
                "title": _text(marketing.get("teaser_headline")) or _text(project.get("title")) or "-",
                "video": _text(marketing.get("teaser_trailer_url")) or "-",
                "description": _text(marketing.get("teaser_excerpt")) or _text(marketing.get("teaser_subtitle")) or "-",
            },
        },
        {
            "id": "audio",
            "label": CHANNEL_LABELS["audio"],
            "description": "Destino seguinte para expansão áudio e editorial complementar.",
            "status": _text((channels.get("audio") or {}).get("manual_status")) or _derive_channel_status(
                ready_signals=len([
                    value for value in [
                        _text(marketing.get("teaser_excerpt")),
                        _text(marketing.get("teaser_cover_url")),
                        _text(marketing.get("teaser_headline")),
                    ] if value
                ]),
                published_signals=False,
                failed_signals=False,
            ),
            "status_meta": _get_status_meta(_text((channels.get("audio") or {}).get("manual_status")) or _derive_channel_status(
                ready_signals=len([
                    value for value in [
                        _text(marketing.get("teaser_excerpt")),
                        _text(marketing.get("teaser_cover_url")),
                        _text(marketing.get("teaser_headline")),
                    ] if value
                ]),
                published_signals=False,
                failed_signals=False,
            )),
            "enabled": bool((channels.get("audio") or {}).get("enabled", True)),
            "detail": "Já existe copy base para preparar uma saída de áudio ou plataforma complementar." if _text(marketing.get("teaser_excerpt")) else "Falta base de texto pública para um canal áudio ficar credível.",
            "attempts": _to_int((channels.get("audio") or {}).get("attempts"), 0),
            "last_attempt": _text((channels.get("audio") or {}).get("last_attempt")) or "-",
            "last_success_at": _text((channels.get("audio") or {}).get("last_success_at")) or "-",
            "last_error": _text((channels.get("audio") or {}).get("last_error")) or "-",
            "notes": _text((channels.get("audio") or {}).get("notes")) or "Preparar áudio final, capa, copy e estado por canal antes de automatizar.",
            "payload_snapshot": {
                "title": _text(marketing.get("teaser_headline")) or _text(project.get("title")) or "-",
                "excerpt": _text(marketing.get("teaser_excerpt")) or "-",
                "cover": _text(marketing.get("teaser_cover_url")) or "-",
            },
        },
    ]

    return destinations


def build_distribution_hub_snapshot(project: Dict[str, Any]) -> Dict[str, Any]:
    marketing = _get_marketing(project)
    website_sync = _get_website_sync(project)
    hub = _get_distribution_hub(project)
    snapshot_time = now_iso()

    return {
        "version": "v6",
        "project_id": _text(project.get("id")),
        "project_title": _text(project.get("title")),
        "saga_name": _text(project.get("saga_name")),
        "public_state": _text(marketing.get("public_state")) or "private",
        "primary_channel": _text(hub.get("primary_channel")) or "website",
        "notes": _text(hub.get("notes")),
        "ready_for_publish": bool(project.get("ready_for_publish")),
        "website_sync": website_sync,
        "marketing": marketing,
        "sales_readiness": _build_sales_readiness(project, marketing, website_sync),
        "destinations": _build_destinations(project, marketing, website_sync, hub),
        "external_outputs": _build_external_outputs(marketing),
        "history": _as_list(hub.get("history")),
        "last_snapshot_at": snapshot_time,
    }


def get_distribution_hub_snapshot(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")
    return build_distribution_hub_snapshot(project)


def _merge_distribution_hub(current_hub: Dict[str, Any], patch: Dict[str, Any], project_id: str) -> Dict[str, Any]:
    merged = {
        "version": "v6",
        "project_id": project_id,
        "primary_channel": _text(current_hub.get("primary_channel")) or "website",
        "notes": _text(current_hub.get("notes")),
        "channels": _normalize_channels(current_hub.get("channels")),
        "history": _as_list(current_hub.get("history")),
        "created_at": _text(current_hub.get("created_at")) or now_iso(),
        "updated_at": now_iso(),
        "last_snapshot_at": _text(current_hub.get("last_snapshot_at")),
    }

    if "primary_channel" in patch:
        merged["primary_channel"] = _text(patch.get("primary_channel")) or merged["primary_channel"]

    if "notes" in patch:
        merged["notes"] = _text(patch.get("notes"))

    if isinstance(patch.get("history"), list):
        merged["history"] = patch["history"]

    if isinstance(patch.get("channels"), dict):
        next_channels = _normalize_channels(merged.get("channels"))
        for channel_id, channel_patch in patch["channels"].items():
            if channel_id not in CHANNEL_LABELS or not isinstance(channel_patch, dict):
                continue
            next_channels[channel_id] = {
                **next_channels[channel_id],
                **channel_patch,
            }
        merged["channels"] = _normalize_channels(next_channels)

    return merged


def patch_distribution_hub(project_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "commercial": {
                **_as_dict(current.get("commercial")),
                "distribution_hub": _merge_distribution_hub(
                    _as_dict(_as_dict(current.get("commercial")).get("distribution_hub")),
                    patch,
                    project_id,
                ),
            },
            "updated_at": now_iso(),
        },
    )

    snapshot = build_distribution_hub_snapshot(updated_project)

    update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "commercial": {
                **_as_dict(current.get("commercial")),
                "distribution_hub": {
                    **_as_dict(_as_dict(current.get("commercial")).get("distribution_hub")),
                    "last_snapshot_at": snapshot.get("last_snapshot_at") or now_iso(),
                    "updated_at": now_iso(),
                },
            },
            "updated_at": now_iso(),
        },
    )

    return snapshot


def refresh_distribution_hub(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    snapshot = build_distribution_hub_snapshot(project)

    update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "commercial": {
                **_as_dict(current.get("commercial")),
                "distribution_hub": {
                    **_get_distribution_hub(current),
                    "version": "v6",
                    "project_id": project_id,
                    "created_at": _text(_get_distribution_hub(current).get("created_at")) or now_iso(),
                    "updated_at": now_iso(),
                    "last_snapshot_at": snapshot.get("last_snapshot_at") or now_iso(),
                },
            },
            "updated_at": now_iso(),
        },
    )

    return snapshot
