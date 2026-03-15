from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, Any, List

from studio_core.services.ip_runtime_service import load_ip_runtime
from studio_core.services.ebook_service import generate_ebook_project
from studio_core.services.audiobook_service import generate_audiobook_project
from studio_core.services.video_service import generate_video_project


EDITORIAL_STATES = [
    "draft",
    "writing",
    "review",
    "approved",
    "producing_ebook",
    "ebook_ready",
    "producing_audio",
    "audio_ready",
    "producing_series",
    "series_ready",
    "ready_for_publish",
    "published"
]


class ProductionPipeline:

    def __init__(self):
        self.logs: List[str] = []
        self.state = "draft"
        self.project_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow().isoformat()

    def log(self, msg: str):
        timestamp = datetime.utcnow().isoformat()
        self.logs.append(f"{timestamp} | {msg}")

    def validate_ip(self, slug: str):
        self.log("Loading IP runtime")
        ip_runtime = load_ip_runtime(slug)
        self.log("IP runtime loaded")
        return ip_runtime

    def move_state(self, new_state: str):
        if new_state not in EDITORIAL_STATES:
            raise ValueError(f"Invalid editorial state: {new_state}")
        self.log(f"State change: {self.state} → {new_state}")
        self.state = new_state

    def produce_ebook(self, project_data: Dict[str, Any]):
        self.move_state("producing_ebook")
        result = generate_ebook_project(project_data)
        self.log("Ebook generated")
        self.move_state("ebook_ready")
        return result

    def produce_audio(self, project_data: Dict[str, Any]):
        self.move_state("producing_audio")
        result = generate_audiobook_project(project_data)
        self.log("Audiobook generated")
        self.move_state("audio_ready")
        return result

    def produce_series(self, project_data: Dict[str, Any]):
        self.move_state("producing_series")
        result = generate_video_project(project_data)
        self.log("Series episode generated")
        self.move_state("series_ready")
        return result

    def ready_for_publish(self):
        self.move_state("ready_for_publish")

    def publish(self):
        self.move_state("published")
        self.log("Project published")

    def get_status(self):
        return {
            "project_id": self.project_id,
            "state": self.state,
            "logs": self.logs,
            "created_at": self.created_at
}
