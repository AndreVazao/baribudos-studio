from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Asset:
    asset_id: str

    project_id: Optional[str]
    ip_slug: str
    series_name: Optional[str]

    publication_id: Optional[str]
    variant_id: Optional[str]

    asset_type: str
    context: str

    language: Optional[str]

    version: int
    is_primary: bool
    priority: int

    width: Optional[int]
    height: Optional[int]

    mime_type: str
    file_size: Optional[int]

    url: str
    storage_path: str

    status: str

    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "project_id": self.project_id,
            "ip_slug": self.ip_slug,
            "series_name": self.series_name,
            "publication_id": self.publication_id,
            "variant_id": self.variant_id,
            "asset_type": self.asset_type,
            "context": self.context,
            "language": self.language,
            "version": self.version,
            "is_primary": self.is_primary,
            "priority": self.priority,
            "width": self.width,
            "height": self.height,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "url": self.url,
            "storage_path": self.storage_path,
            "status": self.status,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "published_at": self.published_at.isoformat() if isinstance(self.published_at, datetime) else self.published_at,
        }
