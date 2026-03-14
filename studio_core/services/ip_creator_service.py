from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import read_json, write_json, update_json_item
from studio_core.core.config import resolve_project_path

IPS_FILE = "data/ip_registry.json"

EDITORIAL_ADMIN_NAMES = {"andré", "andre", "esposa", "wife", "mama"}
EDITORIAL_ADMIN_ROLES = {"owner", "creator", "admin"}


def _studio_sagas_root() -> Path:
    return resolve_project_path("studio", "sagas")


def _safe_slug(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or "").strip())
    slug = "-".join(part for part in slug.split("-") if part)
    return slug or "nova-saga"


def _normalize_name(value: str) -> str:
    return str(value or "").strip().lower()


def get_ip_schema_template() -> Dict[str, Any]:
    return {
        "id": "",
        "slug": "",
        "name": "",
        "owner_id": "",
        "owner_name": "",
        "exclusive": False,
        "visible_to_owner_only": False,
        "editable_by_roles": ["owner", "admin"],
        "publishable_by_roles": ["owner", "admin"],
        "allowed_editor_user_ids": [],
        "allowed_editor_names": [],
        "cloneable": True,
        "status": "draft",
        "default_language": "pt-PT",
        "output_languages": ["pt-PT"],
        "metadata": {
            "author_default": "",
            "producer": "",
            "tagline": "",
            "mission": "",
            "target_age": "",
            "series_name": "",
            "genre": "",
            "description": ""
        },
        "brand_assets": {
            "studio_logo": "",
            "series_logo": "",
            "seal_logo": ""
        },
        "palette": {
            "primary": "#2F5E2E",
            "secondary": "#6FA86A",
            "accent": "#D4A73C",
            "background": "#F5EED6",
            "character_base": "#8B5E3C"
        },
        "main_characters": [],
        "canons": {
            "visual": "visual-canon.json",
            "narrative": "narrative-canon.json",
            "episode": "episode-canon.json",
            "series_arc": "series-arc-canon.json",
            "pedagogical": "pedagogical-canon.json",
            "age_badge": "age-badge-canon.json"
        },
        "created_at": "",
        "updated_at": ""
    }


def _default_baribudos_registry_entry() -> Dict[str, Any]:
    return {
        "id": "ip-baribudos",
        "slug": "baribudos",
        "name": "Os Baribudos",
        "owner_id": "andre-vazao",
        "owner_name": "André Vazão",
        "exclusive": True,
        "visible_to_owner_only": True,
        "editable_by_roles": ["owner", "creator"],
        "publishable_by_roles": ["owner", "creator"],
        "allowed_editor_user_ids": [],
        "allowed_editor_names": ["André Vazão"],
        "cloneable": False,
        "status": "active",
        "default_language": "pt-PT",
        "output_languages": ["pt-PT", "pt-BR", "en", "es", "fr", "de", "it", "nl", "zh", "ja"],
        "metadata": {
            "author_default": "André Vazão",
            "producer": "Baribudos Studio",
            "tagline": "Histórias que Protegem",
            "mission": "Desenvolvimento emocional infantil",
            "target_age": "4-10",
            "series_name": "Os Baribudos",
            "genre": "Infantil Educativo Ilustrado",
            "description": "Coleção educativa emocional com natureza, descoberta e proteção."
        },
        "brand_assets": {
            "studio_logo": "public/brand/baribudos-studio-logo.png",
            "series_logo": "public/brand/os-baribudos-logo.png",
            "seal_logo": "public/brand/historia-que-protege-selo.png"
        },
        "palette": {
            "primary": "#2F5E2E",
            "secondary": "#6FA86A",
            "accent": "#D4A73C",
            "background": "#F5EED6",
            "character_base": "#8B5E3C"
        },
        "main_characters": [
            {"id": "magnus", "name": "Magnus", "role": "father"},
            {"id": "luma", "name": "Luma", "role": "mother"},
            {"id": "roko", "name": "Roko", "role": "child"},
            {"id": "mila", "name": "Mila", "role": "child"},
            {"id": "tilo", "name": "Tilo", "role": "child"}
        ],
        "canons": {
            "visual": "visual-canon.json",
            "narrative": "narrative-canon.json",
            "episode": "episode-canon.json",
            "series_arc": "series-arc-canon.json",
            "pedagogical": "pedagogical-canon.json",
            "age_badge": "age-badge-canon.json"
        },
        "created_at": now_iso(),
        "updated_at": now_iso()
    }


def ensure_ip_registry() -> List[Dict[str, Any]]:
    data = read_json(IPS_FILE, [])
    registry = data if isinstance(data, list) else []

    has_baribudos = any(str(item.get("slug", "")).strip() == "baribudos" for item in registry)
    if not has_baribudos:
        registry.append(_default_baribudos_registry_entry())
        write_json(IPS_FILE, registry)

    return registry


def list_ips() -> List[Dict[str, Any]]:
    return ensure_ip_registry()


def get_ip_by_slug(slug: str) -> Dict[str, Any] | None:
    slug = _safe_slug(slug)
    for item in ensure_ip_registry():
        if str(item.get("slug", "")).strip() == slug:
            return item
    return None


def is_editorial_admin(user: Dict[str, Any] | None) -> bool:
    if not user:
        return False
    role = str(user.get("role", "")).strip().lower()
    name = _normalize_name(user.get("name", ""))
    return role in EDITORIAL_ADMIN_ROLES or name in EDITORIAL_ADMIN_NAMES


def can_view_ip(user: Dict[str, Any] | None, item: Dict[str, Any]) -> bool:
    if not item:
        return False

    if not bool(item.get("visible_to_owner_only", False)):
        return True

    if not user:
        return False

    user_id = str(user.get("id", "")).strip()
    user_name = str(user.get("name", "")).strip()
    owner_id = str(item.get("owner_id", "")).strip()
    owner_name = str(item.get("owner_name", "")).strip()

    return user_id == owner_id or _normalize_name(user_name) == _normalize_name(owner_name)


def list_ips_for_user(user: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    return [item for item in ensure_ip_registry() if can_view_ip(user, item)]


def create_ip(payload: Dict[str, Any]) -> Dict[str, Any]:
    registry = ensure_ip_registry()
    template = get_ip_schema_template()

    name = str(payload.get("name", "")).strip()
    if not name:
        raise ValueError("Nome da IP é obrigatório.")

    slug = _safe_slug(payload.get("slug") or name)
    if get_ip_by_slug(slug):
        raise ValueError("Já existe uma IP com esse slug.")

    owner_id = str(payload.get("owner_id", "")).strip()
    owner_name = str(payload.get("owner_name", "")).strip()

    metadata = {
        **template["metadata"],
        **(payload.get("metadata") or {})
    }

    item = {
        **template,
        "id": str(uuid4()),
        "slug": slug,
        "name": name,
        "owner_id": owner_id,
        "owner_name": owner_name,
        "exclusive": bool(payload.get("exclusive", False)),
        "visible_to_owner_only": bool(payload.get("visible_to_owner_only", False)),
        "editable_by_roles": payload.get("editable_by_roles") or ["owner", "admin"],
        "publishable_by_roles": payload.get("publishable_by_roles") or ["owner", "admin"],
        "allowed_editor_user_ids": payload.get("allowed_editor_user_ids") or [],
        "allowed_editor_names": payload.get("allowed_editor_names") or [],
        "cloneable": bool(payload.get("cloneable", True)),
        "status": str(payload.get("status", "draft")).strip(),
        "default_language": str(payload.get("default_language", "pt-PT")).strip(),
        "output_languages": payload.get("output_languages") or ["pt-PT"],
        "metadata": metadata,
        "brand_assets": payload.get("brand_assets") or template["brand_assets"],
        "palette": payload.get("palette") or template["palette"],
        "main_characters": payload.get("main_characters") or [],
        "created_at": now_iso(),
        "updated_at": now_iso()
    }

    registry.append(item)
    write_json(IPS_FILE, registry)
    ensure_ip_folder_structure(slug)
    return item


def update_ip(slug: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    current = get_ip_by_slug(slug)
    if not current:
        raise ValueError("IP não encontrada.")

    if bool(current.get("exclusive", False)):
        raise ValueError("IP exclusiva protegida. Não pode ser alterada por esta rota.")

    return update_json_item(
        IPS_FILE,
        current["id"],
        lambda item: {
            **item,
            **{k: v for k, v in patch.items() if k not in {"id", "slug", "created_at", "palette", "brand_assets", "metadata"}},
            "palette": {
                **(item.get("palette") or {}),
                **(patch.get("palette") or {})
            },
            "brand_assets": {
                **(item.get("brand_assets") or {}),
                **(patch.get("brand_assets") or {})
            },
            "metadata": {
                **(item.get("metadata") or {}),
                **(patch.get("metadata") or {})
            },
            "updated_at": now_iso()
        }
    )


def can_edit_ip(user: Dict[str, Any] | None, slug: str) -> bool:
    item = get_ip_by_slug(slug)
    if not item or not user:
        return False

    if not can_view_ip(user, item):
        return False

    user_id = str(user.get("id", "")).strip()
    user_name = str(user.get("name", "")).strip()
    role = str(user.get("role", "")).strip()

    if user_id == str(item.get("owner_id", "")).strip():
        return True

    if _normalize_name(user_name) == _normalize_name(item.get("owner_name", "")):
        return True

    if role in set(item.get("editable_by_roles") or []):
        return True

    if user_id and user_id in set(item.get("allowed_editor_user_ids") or []):
        return True

    if user_name and _normalize_name(user_name) in {_normalize_name(x) for x in (item.get("allowed_editor_names") or [])}:
        return True

    return False


def can_publish_ip(user: Dict[str, Any] | None, slug: str) -> bool:
    item = get_ip_by_slug(slug)
    if not item or not user:
        return False

    if not can_view_ip(user, item):
        return False

    if is_editorial_admin(user):
        return True

    role = str(user.get("role", "")).strip()
    user_id = str(user.get("id", "")).strip()
    user_name = str(user.get("name", "")).strip()

    if role in set(item.get("publishable_by_roles") or []):
        return True

    if user_id == str(item.get("owner_id", "")).strip():
        return True

    if _normalize_name(user_name) == _normalize_name(item.get("owner_name", "")):
        return True

    return False


def ensure_ip_folder_structure(slug: str) -> str:
    root = _studio_sagas_root() / slug
    root.mkdir(parents=True, exist_ok=True)

    files = {
        "visual-canon.json": {
            "ip": slug,
            "style": {},
            "color_palette": {},
            "cover_rules": {}
        },
        "narrative-canon.json": {
            "ip": slug,
            "core_identity": {},
            "narrative_structure_standard": []
        },
        "episode-canon.json": {
            "ip": slug,
            "episode_format": {},
            "scene_structure_standard": []
        },
        "series-arc-canon.json": {
            "ip": slug,
            "series_model": "continuous_growth"
        },
        "pedagogical-canon.json": {
            "ip": slug,
            "pedagogical_mission": {},
            "approved_values": []
        },
        "age-badge-canon.json": {
            "ip": slug,
            "design_rules": {},
            "color_rules": {}
        },
        "characters-master.json": {
            "visual_dna": {},
            "family": []
        }
    }

    for file_name, default_content in files.items():
        target = root / file_name
        if not target.exists():
            target.write_text(json.dumps(default_content, ensure_ascii=False, indent=2), encoding="utf-8")

    return str(root)


def list_ip_assets_schema() -> Dict[str, Any]:
    return {
        "badge_editor": True,
        "seal_editor": True,
        "logo_editor": True,
        "palette_editor": True,
        "character_editor": True,
        "canon_builder": True,
        "metadata_editor": True
}
