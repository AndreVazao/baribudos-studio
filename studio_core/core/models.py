from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_website_marketing() -> Dict[str, Any]:
    return {
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


def default_distribution_channel(enabled: bool = True) -> Dict[str, Any]:
    return {
        "enabled": enabled,
        "manual_status": "",
        "attempts": 0,
        "last_attempt": "",
        "last_success_at": "",
        "last_error": "",
        "notes": "",
    }


def default_distribution_hub() -> Dict[str, Any]:
    return {
        "version": "v6",
        "project_id": "",
        "primary_channel": "website",
        "notes": "",
        "channels": {
            "website": default_distribution_channel(True),
            "amazon": default_distribution_channel(True),
            "youtube": default_distribution_channel(True),
            "audio": default_distribution_channel(True),
        },
        "history": [],
        "created_at": "",
        "updated_at": "",
        "last_snapshot_at": "",
    }


def default_project_commercial() -> Dict[str, Any]:
    return {
        "internal_code": "",
        "isbn": "",
        "asin": "",
        "price": "",
        "currency": "EUR",
        "collection_seal": "",
        "marketplaces": [],
        "commercial_status": "draft",
        "channels": [],
        "keywords": [],
        "subtitle": "",
        "blurb": "",
        "website_marketing": default_website_marketing(),
        "distribution_hub": default_distribution_hub(),
    }


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    role: Literal["owner", "creator", "admin", "editor", "voice-recorder", "child", "viewer"] = "editor"
    pin: str = Field(min_length=1, max_length=20)
    is_active: bool = True


class UserPatch(BaseModel):
    name: Optional[str] = None
    role: Optional[Literal["owner", "creator", "admin", "editor", "voice-recorder", "child", "viewer"]] = None
    is_active: Optional[bool] = None


class UserPinPatch(BaseModel):
    pin: str = Field(min_length=1, max_length=20)


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    role: str
    pin: str
    is_active: bool = True
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)


DEFAULT_STAGE_MODES = {
    "story_input_mode": "manual",
    "illustration_mode": "manual",
    "audio_mode": "manual",
    "video_mode": "manual",
}


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    saga_slug: str = "baribudos"
    saga_name: str = "Baribudos"
    language: str = "pt-PT"
    output_languages: List[str] = Field(default_factory=lambda: ["pt-PT"])
    created_by: str = ""
    created_by_name: str = ""
    visible_to_owner_only: bool = True
    project_mode: str = "official"
    parent_project_id: str = ""
    continuity_source_project_id: str = ""
    hidden_universe_key: str = ""
    hidden_universe_name: str = ""
    hidden_saga_key: str = ""
    hidden_saga_name: str = ""
    stage_modes: Dict[str, Any] = Field(default_factory=lambda: dict(DEFAULT_STAGE_MODES))
    ready_for_publish: bool = False
    website_sync: Dict[str, Any] = Field(default_factory=dict)


class ProjectPatch(BaseModel):
    title: Optional[str] = None
    saga_slug: Optional[str] = None
    saga_name: Optional[str] = None
    language: Optional[str] = None
    output_languages: Optional[List[str]] = None
    status: Optional[str] = None
    editorial_status: Optional[str] = None
    front_matter: Optional[Dict[str, Any]] = None
    story: Optional[Dict[str, Any]] = None
    cover_image: Optional[str] = None
    illustration_path: Optional[str] = None
    commercial: Optional[Dict[str, Any]] = None
    project_mode: Optional[str] = None
    parent_project_id: Optional[str] = None
    continuity_source_project_id: Optional[str] = None
    hidden_universe_key: Optional[str] = None
    hidden_universe_name: Optional[str] = None
    hidden_saga_key: Optional[str] = None
    hidden_saga_name: Optional[str] = None
    continuity: Optional[Dict[str, Any]] = None
    stage_modes: Optional[Dict[str, Any]] = None
    ready_for_publish: Optional[bool] = None
    website_sync: Optional[Dict[str, Any]] = None


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    saga_slug: str
    saga_name: str
    language: str = "pt-PT"
    output_languages: List[str] = Field(default_factory=lambda: ["pt-PT"])
    status: str = "draft"
    editorial_status: str = "draft"
    created_by: str = ""
    created_by_name: str = ""
    visible_to_owner_only: bool = True
    project_mode: str = "official"
    parent_project_id: str = ""
    continuity_source_project_id: str = ""
    hidden_universe_key: str = ""
    hidden_universe_name: str = ""
    hidden_saga_key: str = ""
    hidden_saga_name: str = ""
    stage_modes: Dict[str, Any] = Field(default_factory=lambda: dict(DEFAULT_STAGE_MODES))
    continuity: Dict[str, Any] = Field(default_factory=lambda: {
        "can_promote_to_official_ip": True,
        "officialization_status": "hidden",
        "suggested_title_origin": "manual_or_future_ai",
        "continuity_character_names": [],
        "continuity_notes": "",
    })
    cover_image: str = ""
    illustration_path: str = ""
    commercial: Dict[str, Any] = Field(default_factory=default_project_commercial)
    front_matter: Dict[str, Any] = Field(default_factory=dict)
    story: Dict[str, Any] = Field(default_factory=lambda: {
        "title": "",
        "language": "pt-PT",
        "pages": [],
        "raw_text": "",
    })
    outputs: Dict[str, Any] = Field(default_factory=dict)
    ready_for_publish: bool = False
    website_sync: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
