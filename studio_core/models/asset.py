from dataclasses import dataclass
from typing import Optional
from datetime import datetime


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
