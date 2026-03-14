from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    saga_slug: str = "baribudos"
    saga_name: str = "Baribudos"
    language: str = "pt-PT"
    output_languages: List[str] = Field(default_factory=lambda: ["pt-PT"])
    created_by: str = ""
    created_by_name: str = ""
    visible_to_owner_only: bool = True


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
    front_matter: Dict[str, Any] = Field(default_factory=dict)
    story: Dict[str, Any] = Field(default_factory=lambda: {
        "title": "",
        "language": "pt-PT",
        "pages": [],
        "raw_text": ""
    })
    outputs: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
