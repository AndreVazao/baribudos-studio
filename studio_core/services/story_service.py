from __future__ import annotations

from typing import Any, Dict
from studio_core.services.story_generation_engine import generate_canon_story


def generate_story(payload: Dict[str, Any]) -> Dict[str, Any]:
    return generate_canon_story(payload)


def generate_volume_guide(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return a blocked state until five authenticated editorial decisions exist.

    The legacy caller supplies one mutable project/story object. That object is
    not an approval authority and cannot satisfy the five-story volume rule.
    Keep the historical id/title/content keys for client compatibility, but do
    not manufacture a guide from a single story or client-supplied flags.
    """
    return {
        "id": "",
        "title": "",
        "content": "",
        "status": "waiting_for_five_approved_stories",
        "generated": False,
        "required_story_count": 5,
        "eligible_story_count": 0,
        "reason": "authenticated_editorial_approval_service_unavailable",
    }
