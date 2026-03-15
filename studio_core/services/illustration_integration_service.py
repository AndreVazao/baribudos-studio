from __future__ import annotations

from typing import Any, Dict, List

from studio_core.services.illustration_asset_service import build_storyboard_manifest, list_approved_frames


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def build_page_illustration_map(project: Dict[str, Any], language: str = "") -> Dict[int, Dict[str, Any]]:
    approved_frames = list_approved_frames(project)
    result: Dict[int, Dict[str, Any]] = {}

    for frame in approved_frames:
        page_number = int(_safe_dict(frame).get("page_number", 0) or 0)
        if page_number <= 0:
            continue

        frame_type = str(_safe_dict(frame).get("frame_type", "")).strip()

        current = result.get(page_number)
        if current is None:
            result[page_number] = frame
            continue

        current_type = str(_safe_dict(current).get("frame_type", "")).strip()

        priority = {
            "book_page": 4,
            "marketing": 3,
            "storyboard": 2,
            "animatic": 1,
        }

        if priority.get(frame_type, 0) > priority.get(current_type, 0):
            result[page_number] = frame

    return result


def enrich_story_pages_with_illustrations(project: Dict[str, Any], story: Dict[str, Any]) -> Dict[str, Any]:
    story = _safe_dict(story)
    pages = _safe_list(story.get("pages", []))
    illustration_map = build_page_illustration_map(project, str(story.get("language", "")).strip())

    enriched_pages = []
    for raw_page in pages:
        page = _safe_dict(raw_page)
        page_number = int(page.get("pageNumber", 0) or 0)
        frame = _safe_dict(illustration_map.get(page_number, {}))

        enriched_pages.append({
            **page,
            "illustration_path": str(frame.get("image_path", "")).strip(),
            "illustration_frame_id": str(frame.get("id", "")).strip(),
            "illustration_frame_type": str(frame.get("frame_type", "")).strip(),
            "has_illustration": bool(str(frame.get("image_path", "")).strip()),
        })

    return {
        **story,
        "pages": enriched_pages,
    }


def build_video_frame_sequence(project: Dict[str, Any]) -> Dict[str, Any]:
    manifest = build_storyboard_manifest(project)
    frames = _safe_list(manifest.get("frames", []))

    sequence = []
    for index, raw_frame in enumerate(frames, start=1):
        frame = _safe_dict(raw_frame)
        image_path = str(frame.get("image_path", "")).strip()
        if not image_path:
            continue

        sequence.append({
            "index": index,
            "frame_id": str(frame.get("frame_id", "")).strip(),
            "page_number": int(frame.get("page_number", 0) or 0),
            "page_title": str(frame.get("page_title", "")).strip(),
            "frame_type": str(frame.get("frame_type", "")).strip(),
            "image_path": image_path,
            "prompt": str(frame.get("prompt", "")).strip(),
        })

    return {
        "project_id": project.get("id", ""),
        "project_title": project.get("title", ""),
        "frames_count": len(sequence),
        "frames": sequence,
}
