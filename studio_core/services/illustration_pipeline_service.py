from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.core.models import now_iso
from studio_core.core.storage import append_json_item, read_json, update_json_item
from studio_core.services.saga_runtime_service import load_saga_runtime

PROJECTS_FILE = "data/projects.json"
ILLUSTRATION_RUNS_FILE = "data/illustration_runs.json"

ILLUSTRATION_MODES = {
    "auto",
    "approval",
    "manual",
    "hybrid",
}

FRAME_TYPES = {
    "book_page",
    "storyboard",
    "marketing",
    "animatic",
}


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _normalize_mode(value: str) -> str:
    mode = str(value or "").strip().lower()
    return mode if mode in ILLUSTRATION_MODES else "approval"


def _normalize_frame_type(value: str) -> str:
    frame_type = str(value or "").strip().lower()
    return frame_type if frame_type in FRAME_TYPES else "book_page"


def _get_project(project_id: str) -> Dict[str, Any] | None:
    projects = read_json(PROJECTS_FILE, [])
    for project in projects:
        if str(project.get("id", "")).strip() == str(project_id).strip():
            return project
    return None


def _extract_family(runtime: Dict[str, Any]) -> List[Dict[str, Any]]:
    canons = _safe_dict(runtime.get("canons", {}))
    characters = _safe_dict(canons.get("characters", {}))
    family = _safe_list(characters.get("family", []))
    return [item for item in family if isinstance(item, dict)]


def _pick_character_names(runtime: Dict[str, Any], story: Dict[str, Any]) -> List[str]:
    protagonist = str(story.get("protagonist", "")).strip()
    support = str(story.get("support_character", "")).strip()

    names = []
    if protagonist:
        names.append(protagonist)
    if support and support not in names:
        names.append(support)

    if names:
        return names

    family = _extract_family(runtime)
    result = []
    for item in family[:2]:
        name = str(item.get("name", "")).strip()
        if name:
            result.append(name)

    return result or ["Tilo"]


def _build_style_reference(runtime: Dict[str, Any]) -> str:
    canons = _safe_dict(runtime.get("canons", {}))
    visual = _safe_dict(canons.get("visual", {}))
    metadata = _safe_dict(runtime.get("metadata", {}))
    palette = _safe_dict(runtime.get("palette", {}))

    style_bits = []

    style = str(visual.get("style", "")).strip()
    if style:
        style_bits.append(style)

    emotional_tone = _safe_list(visual.get("emotional_tone", []))
    if emotional_tone:
        style_bits.append("emotion tone: " + ", ".join(str(item).strip() for item in emotional_tone if str(item).strip()))

    environment = _safe_dict(visual.get("environment_rules", {}))
    world = str(environment.get("world", "")).strip()
    atmosphere = str(environment.get("atmosphere", "")).strip()
    if world:
        style_bits.append(f"world: {world}")
    if atmosphere:
        style_bits.append(f"atmosphere: {atmosphere}")

    lighting = _safe_dict(visual.get("lighting_rules", {}))
    lighting_type = str(lighting.get("type", "")).strip()
    temperature = str(lighting.get("temperature", "")).strip()
    if lighting_type or temperature:
        style_bits.append(f"lighting: {lighting_type} {temperature}".strip())

    style_bits.append(
        "palette: "
        f"primary={palette.get('primary', '')}, "
        f"secondary={palette.get('secondary', '')}, "
        f"accent={palette.get('accent', '')}, "
        f"background={palette.get('background', '')}, "
        f"character_base={palette.get('character_base', '')}"
    )

    target_age = str(metadata.get("target_age", "")).strip()
    if target_age:
        style_bits.append(f"target age: {target_age}")

    return " | ".join(bit for bit in style_bits if bit).strip()


def _scene_prompt(
    *,
    runtime: Dict[str, Any],
    project: Dict[str, Any],
    story: Dict[str, Any],
    page: Dict[str, Any],
    frame_type: str,
) -> str:
    project_title = str(project.get("title", "Projeto")).strip() or "Projeto"
    page_title = str(page.get("title", "")).strip()
    page_text = str(page.get("text", "")).strip()
    characters = ", ".join(_pick_character_names(runtime, story))
    series_name = str(runtime.get("name", "")).strip() or "Saga"
    style_reference = _build_style_reference(runtime)

    base = (
        f"Project: {project_title}. "
        f"Series/IP: {series_name}. "
        f"Frame type: {frame_type}. "
        f"Characters visible: {characters}. "
        f"Scene title: {page_title}. "
        f"Scene narrative: {page_text}. "
        f"Style reference: {style_reference}. "
        f"Keep visual canon consistency. "
        f"Children's book composition. "
        f"High readability. "
        f"Leave breathing space for text when needed."
    )

    if frame_type == "storyboard":
        base += " Compose as storyboard frame, clear action pose, cinematic framing, motion-friendly composition."
    elif frame_type == "marketing":
        base += " Compose as hero marketing frame, stronger focal point, richer visual impact."
    elif frame_type == "animatic":
        base += " Compose as animation-ready frame, clean silhouette, simple staging, readable depth."
    else:
        base += " Compose as editorial book page illustration."

    return " ".join(base.split()).strip()


def _build_frame_entry(
    *,
    runtime: Dict[str, Any],
    project: Dict[str, Any],
    story: Dict[str, Any],
    page: Dict[str, Any],
    mode: str,
    frame_type: str,
    selected: bool,
) -> Dict[str, Any]:
    page_number = int(page.get("pageNumber", 0) or 0)
    status = "pending_approval" if mode == "approval" and selected else "planned"
    if mode == "manual" and selected:
        status = "awaiting_upload"

    return {
        "id": str(uuid4()),
        "page_number": page_number,
        "page_title": str(page.get("title", "")).strip(),
        "frame_type": frame_type,
        "selected": bool(selected),
        "mode": mode,
        "status": status,
        "prompt": _scene_prompt(
            runtime=runtime,
            project=project,
            story=story,
            page=page,
            frame_type=frame_type,
        ) if selected else "",
        "image_path": "",
        "approved": False,
        "uploaded_manually": False,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }


def _resolve_selected_pages(story: Dict[str, Any], payload: Dict[str, Any]) -> List[int]:
    explicit = payload.get("selected_pages")
    if isinstance(explicit, list) and explicit:
        result = []
        for item in explicit:
            try:
                result.append(int(item))
            except Exception:
                continue
        if result:
            return sorted(set(result))

    mode = _normalize_mode(payload.get("mode", "approval"))
    pages = _safe_list(story.get("pages", []))

    if mode in {"auto", "approval", "hybrid"}:
        return [int(_safe_dict(page).get("pageNumber", idx + 1)) for idx, page in enumerate(pages)]

    return []


def _resolve_frame_plan(mode: str) -> List[str]:
    if mode == "hybrid":
        return ["book_page", "storyboard"]
    return ["book_page"]


def setup_illustration_pipeline(project_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    mode = _normalize_mode(payload.get("mode", "approval"))
    project_title = str(project.get("title", "Projeto")).strip() or "Projeto"
    runtime = load_saga_runtime(str(project.get("saga_slug", "baribudos")).strip() or "baribudos")

    language = str(payload.get("language", project.get("language", runtime.get("default_language", "pt-PT")))).strip() or "pt-PT"
    story_variants = _safe_dict(project.get("language_variants", {}))
    story = _safe_dict(story_variants.get(language, {}))
    if not story:
        story = _safe_dict(project.get("story", {}))

    pages = _safe_list(story.get("pages", []))
    if not pages:
        raise ValueError("Projeto sem páginas narrativas para ilustrar.")

    selected_pages = _resolve_selected_pages(story, payload)
    frame_plan = _resolve_frame_plan(mode)

    frames: List[Dict[str, Any]] = []
    for idx, raw_page in enumerate(pages, start=1):
        page = _safe_dict(raw_page)
        page_number = int(page.get("pageNumber", idx) or idx)
        selected = page_number in selected_pages

        for frame_type in frame_plan:
            frames.append(
                _build_frame_entry(
                    runtime=runtime,
                    project=project,
                    story=story,
                    page=page,
                    mode=mode,
                    frame_type=frame_type,
                    selected=selected,
                )
            )

    pipeline = {
        "id": str(uuid4()),
        "project_id": project_id,
        "project_title": project_title,
        "runtime_slug": runtime.get("slug", ""),
        "runtime_name": runtime.get("name", ""),
        "language": language,
        "mode": mode,
        "selected_pages": selected_pages,
        "frame_plan": frame_plan,
        "frames": frames,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "illustration_pipeline": pipeline,
            "updated_at": now_iso(),
        }
    )

    append_json_item(ILLUSTRATION_RUNS_FILE, {
        "id": pipeline["id"],
        "project_id": project_id,
        "mode": mode,
        "language": language,
        "frames_count": len(frames),
        "created_at": now_iso(),
    })

    return {
        "ok": True,
        "pipeline": pipeline,
        "project": updated_project,
    }


def update_illustration_frame_status(
    project_id: str,
    frame_id: str,
    *,
    status: str | None = None,
    approved: bool | None = None,
    image_path: str | None = None,
    uploaded_manually: bool | None = None,
) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")

    pipeline = _safe_dict(project.get("illustration_pipeline", {}))
    frames = _safe_list(pipeline.get("frames", []))
    if not frames:
        raise ValueError("Projeto sem pipeline de ilustração.")

    updated = False
    next_frames = []

    for item in frames:
        frame = _safe_dict(item)
        if str(frame.get("id", "")).strip() != str(frame_id).strip():
            next_frames.append(frame)
            continue

        next_frame = {
            **frame,
            "status": str(status).strip() if status is not None else frame.get("status", "planned"),
            "approved": bool(approved) if approved is not None else bool(frame.get("approved", False)),
            "image_path": str(image_path).strip() if image_path is not None else str(frame.get("image_path", "")).strip(),
            "uploaded_manually": bool(uploaded_manually) if uploaded_manually is not None else bool(frame.get("uploaded_manually", False)),
            "updated_at": now_iso(),
        }
        next_frames.append(next_frame)
        updated = True

    if not updated:
        raise ValueError("Frame não encontrado.")

    updated_project = update_json_item(
        PROJECTS_FILE,
        project_id,
        lambda current: {
            **current,
            "illustration_pipeline": {
                **_safe_dict(current.get("illustration_pipeline", {})),
                "frames": next_frames,
                "updated_at": now_iso(),
            },
            "updated_at": now_iso(),
        }
    )

    return {
        "ok": True,
        "project": updated_project,
        "illustration_pipeline": _safe_dict(updated_project.get("illustration_pipeline", {})),
    }


def get_project_illustration_pipeline(project_id: str) -> Dict[str, Any]:
    project = _get_project(project_id)
    if not project:
        raise ValueError("Projeto não encontrado.")
    return _safe_dict(project.get("illustration_pipeline", {}))


def list_illustration_runs() -> List[Dict[str, Any]]:
    runs = read_json(ILLUSTRATION_RUNS_FILE, [])
    return runs if isinstance(runs, list) else []
