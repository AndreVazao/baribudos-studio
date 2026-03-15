from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.services.saga_runtime_service import load_saga_runtime


DEFAULT_STRUCTURE = [
    "simple_introduction",
    "strange_element_or_problem",
    "emotional_questioning",
    "gentle_guidance_or_reflection",
    "progressive_transformation",
    "implicit_moral",
    "final_strong_sentence",
]


def _normalize_text(value: str) -> str:
    return " ".join(str(value or "").replace("\n", " ").split()).strip()


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _pick_main_character(runtime: Dict[str, Any], preferred_name: str = "") -> Dict[str, Any]:
    preferred_name = str(preferred_name or "").strip().lower()

    main_characters = _safe_list(runtime.get("main_characters", []))
    family = _safe_list(_safe_dict(runtime.get("canons", {})).get("characters", {}).get("family", []))

    pool: List[Dict[str, Any]] = []
    for item in main_characters:
        if isinstance(item, dict):
            pool.append(item)
    for item in family:
        if isinstance(item, dict):
            pool.append(item)

    if preferred_name:
        for item in pool:
            if str(item.get("name", "")).strip().lower() == preferred_name:
                return item

    for item in pool:
        if str(item.get("name", "")).strip():
            return item

    return {
        "id": "hero-default",
        "name": "Tilo",
        "role": "child",
        "description": "",
    }


def _pick_support_character(runtime: Dict[str, Any], protagonist_name: str) -> Dict[str, Any]:
    protagonist_name = str(protagonist_name or "").strip().lower()

    family = _safe_list(_safe_dict(runtime.get("canons", {})).get("characters", {}).get("family", []))
    for item in family:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        if name.lower() != protagonist_name:
            return item

    main_characters = _safe_list(runtime.get("main_characters", []))
    for item in main_characters:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        if name.lower() != protagonist_name:
            return item

    return {
        "id": "mentor-default",
        "name": "Magnus",
        "role": "mentor",
        "description": "",
    }


def _pick_value_theme(runtime: Dict[str, Any], preferred_value: str = "") -> str:
    preferred_value = str(preferred_value or "").strip()
    if preferred_value:
        return preferred_value

    pedagogical = _safe_dict(_safe_dict(runtime.get("canons", {})).get("pedagogical", {}))
    values_pool = _safe_list(pedagogical.get("approved_values", []))

    for item in values_pool:
        if isinstance(item, dict):
            label = str(item.get("label", "")).strip()
            if label:
                return label
        else:
            text = str(item or "").strip()
            if text:
                return text

    narrative = _safe_dict(_safe_dict(runtime.get("canons", {})).get("narrative", {}))
    values_pool = _safe_list(narrative.get("values_pool", []))
    for item in values_pool:
        if isinstance(item, dict):
            label = str(item.get("label", "")).strip()
            if label:
                return label
        else:
            text = str(item or "").strip()
            if text:
                return text

    return "Coragem"


def _pick_final_phrase(runtime: Dict[str, Any]) -> str:
    narrative = _safe_dict(_safe_dict(runtime.get("canons", {})).get("narrative", {}))
    final_phrase_rule = narrative.get("final_phrase_rule", "")

    if isinstance(final_phrase_rule, dict):
        phrase = str(final_phrase_rule.get("default_phrase", "")).strip()
        if phrase:
            return phrase

    phrase = str(final_phrase_rule or "").strip()
    if phrase:
        return phrase

    return "Na dúvida, escolhe o caminho seguro."


def _pick_narrative_structure(runtime: Dict[str, Any]) -> List[str]:
    narrative = _safe_dict(_safe_dict(runtime.get("canons", {})).get("narrative", {}))
    structure = _safe_list(narrative.get("narrative_structure_standard", []))

    normalized = [str(item or "").strip() for item in structure if str(item or "").strip()]
    return normalized or DEFAULT_STRUCTURE


def _pick_world_name(runtime: Dict[str, Any]) -> str:
    resolved = _safe_dict(runtime.get("resolved", {}))
    series_name = str(resolved.get("series_name", "")).strip()
    if series_name:
        return series_name
    return str(runtime.get("name", "Saga")).strip() or "Saga"


def _build_scene_text(
    scene_key: str,
    *,
    title: str,
    world_name: str,
    protagonist: str,
    support: str,
    value_theme: str,
    mission: str,
    final_phrase: str,
) -> str:
    scene_key = str(scene_key or "").strip()

    templates = {
        "simple_introduction": (
            f"{protagonist} vivia dias calmos no universo de {world_name}. "
            f"Naquela manhã, tudo parecia normal, mas no coração sentia que algo novo estava prestes a acontecer."
        ),
        "strange_element_or_problem": (
            f"Foi então que, em '{title}', apareceu um sinal estranho no caminho. "
            f"{protagonist} não percebeu logo se aquilo era seguro ou se podia trazer problemas."
        ),
        "emotional_questioning": (
            f"{protagonist} parou e pensou no que estava a sentir. "
            f"Havia curiosidade, mas também uma pequena dúvida que não queria ser ignorada."
        ),
        "gentle_guidance_or_reflection": (
            f"Antes de decidir, {protagonist} procurou {support}. "
            f"Com palavras calmas e sem medo, veio um momento de reflexão sobre {value_theme} e {mission or 'crescimento interior'}."
        ),
        "progressive_transformation": (
            f"Pouco a pouco, {protagonist} começou a ver melhor a situação. "
            f"Em vez de agir depressa, escolheu observar, respirar fundo e dar um passo de cada vez."
        ),
        "implicit_moral": (
            f"No final, sem grandes sermões, ficou claro que {value_theme.lower()} ajuda a proteger melhor. "
            f"As boas escolhas crescem quando se pensa com calma."
        ),
        "final_strong_sentence": final_phrase,
    }

    return templates.get(
        scene_key,
        f"{protagonist} continuou a aprender no universo de {world_name}."
    )


def _split_pages_from_scenes(
    title: str,
    scenes: List[Dict[str, Any]],
    max_scenes_per_page: int = 1,
) -> List[Dict[str, Any]]:
    pages: List[Dict[str, Any]] = []
    current: List[str] = []
    page_number = 1

    for scene in scenes:
        current.append(str(scene.get("text", "")).strip())
        if len(current) >= max_scenes_per_page:
            pages.append({
                "id": str(uuid4()),
                "pageNumber": page_number,
                "title": f"{title} — Página {page_number}",
                "text": "\n\n".join(part for part in current if part).strip(),
            })
            current = []
            page_number += 1

    if current:
        pages.append({
            "id": str(uuid4()),
            "pageNumber": page_number,
            "title": f"{title} — Página {page_number}",
            "text": "\n\n".join(part for part in current if part).strip(),
        })

    return pages


def generate_canon_story(payload: Dict[str, Any]) -> Dict[str, Any]:
    saga_id = str(payload.get("saga_id", "baribudos")).strip()
    title = str(payload.get("title", "Nova História")).strip() or "Nova História"
    language = str(payload.get("language", "pt-PT")).strip() or "pt-PT"

    runtime = load_saga_runtime(saga_id)
    resolved = _safe_dict(runtime.get("resolved", {}))

    protagonist_data = _pick_main_character(runtime, payload.get("protagonist", ""))
    protagonist = str(protagonist_data.get("name", "Tilo")).strip() or "Tilo"

    support_data = _pick_support_character(runtime, protagonist)
    support = str(support_data.get("name", "Magnus")).strip() or "Magnus"

    value_theme = _pick_value_theme(runtime, payload.get("value_theme", ""))
    final_phrase = _pick_final_phrase(runtime)
    structure = _pick_narrative_structure(runtime)
    world_name = _pick_world_name(runtime)
    mission = str(resolved.get("mission", "")).strip()

    custom_raw_text = _normalize_text(payload.get("raw_text", ""))
    if custom_raw_text:
        pages = [{
            "id": str(uuid4()),
            "pageNumber": 1,
            "title": f"{title} — Página 1",
            "text": custom_raw_text,
        }]
        scenes = [{
            "id": str(uuid4()),
            "key": "custom_raw_text",
            "text": custom_raw_text,
        }]
        raw_text = custom_raw_text
    else:
        scenes = []
        for scene_key in structure:
            scene_text = _build_scene_text(
                scene_key,
                title=title,
                world_name=world_name,
                protagonist=protagonist,
                support=support,
                value_theme=value_theme,
                mission=mission,
                final_phrase=final_phrase,
            )
            scenes.append({
                "id": str(uuid4()),
                "key": scene_key,
                "text": scene_text,
            })

        pages = _split_pages_from_scenes(title, scenes, max_scenes_per_page=1)
        raw_text = " ".join(scene["text"] for scene in scenes).strip()

    return {
        "id": str(uuid4()),
        "title": title,
        "language": language,
        "saga_id": saga_id,
        "series_name": resolved.get("series_name", runtime.get("name", "")),
        "tagline": resolved.get("tagline", ""),
        "mission": resolved.get("mission", ""),
        "target_age": resolved.get("target_age", ""),
        "genre": resolved.get("genre", ""),
        "description": resolved.get("description", ""),
        "protagonist": protagonist,
        "support_character": support,
        "value_theme": value_theme,
        "final_phrase": final_phrase,
        "structure": structure,
        "scenes": scenes,
        "main_characters": runtime.get("main_characters", []),
        "runtime_validation": runtime.get("validation", {}),
        "raw_text": raw_text,
        "pages": pages,
  }
