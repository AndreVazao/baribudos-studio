from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

from studio_core.services.ip_runtime_service import load_ip_runtime


def _normalize_text(text: str) -> str:
    return " ".join(str(text or "").replace("\n", " ").split()).strip()


def _split_story_into_pages(text: str, max_words_per_page: int = 35) -> List[Dict[str, Any]]:
    words = _normalize_text(text).split()
    if not words:
        return []

    pages: List[Dict[str, Any]] = []
    chunk: List[str] = []
    page_number = 1

    for word in words:
        chunk.append(word)
        if len(chunk) >= max_words_per_page:
            pages.append({
                "id": str(uuid4()),
                "pageNumber": page_number,
                "title": f"Página {page_number}",
                "text": " ".join(chunk).strip()
            })
            page_number += 1
            chunk = []

    if chunk:
        pages.append({
            "id": str(uuid4()),
            "pageNumber": page_number,
            "title": f"Página {page_number}",
            "text": " ".join(chunk).strip()
        })

    return pages


def _default_structure_from_canon(saga_id: str) -> List[str]:
    try:
        runtime = load_ip_runtime(saga_id)
        canon = runtime.get("canons", {}).get("narrative", {}) or {}
        return canon.get("narrative_structure_standard", [])
    except Exception:
        return [
            "simple_introduction",
            "strange_element_or_problem",
            "emotional_questioning",
            "gentle_guidance_or_reflection",
            "progressive_transformation",
            "implicit_moral",
            "final_strong_sentence"
        ]


def _default_final_phrase_from_canon(saga_id: str) -> str:
    try:
        runtime = load_ip_runtime(saga_id)
        canon = runtime.get("canons", {}).get("narrative", {}) or {}
        final_rule = canon.get("final_phrase_rule", {})
        if isinstance(final_rule, dict):
            return str(final_rule.get("default_phrase", "Na dúvida, escolhe o caminho seguro.")).strip()
        if isinstance(final_rule, str):
            return final_rule.strip()
    except Exception:
        pass
    return "Na dúvida, escolhe o caminho seguro."


def _default_value_from_canon(saga_id: str) -> str:
    try:
        runtime = load_ip_runtime(saga_id)
        canon = runtime.get("canons", {}).get("pedagogical", {}) or {}
        values_pool = canon.get("approved_values", [])
        if values_pool:
            first = values_pool[0]
            if isinstance(first, dict):
                return str(first.get("label", "Coragem")).strip()
            return str(first).strip()
    except Exception:
        pass
    return "Coragem"


def _default_protagonist(saga_id: str) -> str:
    try:
        runtime = load_ip_runtime(saga_id)
        chars = runtime.get("main_characters", []) or []
        if chars:
            return str(chars[0].get("name", "Herói")).strip()
    except Exception:
        pass
    return "Tilo"


def _default_story_text(payload: Dict[str, Any]) -> str:
    saga_id = str(payload.get("saga_id", "baribudos")).strip()
    title = str(payload.get("title", "Nova História")).strip()
    saga_name = str(payload.get("saga_name", "Os Baribudos")).strip()
    protagonist = str(payload.get("protagonist", _default_protagonist(saga_id))).strip()
    value_theme = str(payload.get("value_theme", _default_value_from_canon(saga_id))).strip()
    final_phrase = _default_final_phrase_from_canon(saga_id)

    return (
        f"{protagonist} acordou cedo no universo de {saga_name}. "
        f"Nesse dia, algo estranho chamou a sua atenção. "
        f"Sentiu curiosidade, mas também uma pequena dúvida no coração. "
        f"Com calma, observou melhor, respirou fundo e decidiu não avançar sem pensar. "
        f"Depois de conversar com quem o ajuda a crescer, compreendeu uma lição sobre {value_theme}. "
        f"No final, voltou para casa mais sereno, mais atento e mais seguro. "
        f"{final_phrase}"
    )


def generate_story(payload: Dict[str, Any]) -> Dict[str, Any]:
    title = str(payload.get("title", "Nova História")).strip()
    language = str(payload.get("language", "pt-PT")).strip()
    saga_id = str(payload.get("saga_id", "baribudos")).strip()

    raw_text = _normalize_text(
        payload.get("raw_text")
        or payload.get("input", {}).get("raw_text")
        or _default_story_text(payload)
    )

    pages = _split_story_into_pages(
        raw_text,
        max_words_per_page=int(payload.get("max_words_per_page", 35))
    )

    runtime = load_ip_runtime(saga_id)
    return {
        "id": str(uuid4()),
        "title": title,
        "language": language,
        "saga_id": saga_id,
        "main_characters": runtime.get("main_characters", []),
        "raw_text": raw_text,
        "structure": _default_structure_from_canon(saga_id),
        "pages": pages
    }


def generate_volume_guide(payload: Dict[str, Any]) -> Dict[str, Any]:
    project_title = str(payload.get("project_title", "Projeto")).strip()
    story = payload.get("story", {}) or {}
    story_title = str(story.get("title", project_title)).strip()
    page_count = len(story.get("pages", []) or [])
    saga_id = str(story.get("saga_id", "baribudos")).strip()
    final_phrase = _default_final_phrase_from_canon(saga_id)

    content = (
        f"Guia do volume: {story_title}\n\n"
        f"Este volume foi preparado para leitura calma e partilhada.\n"
        f"Número de páginas: {page_count}\n"
        f"Objetivo emocional: promover conversa segura entre criança e família.\n\n"
        f"Sugestão de uso:\n"
        f"- Ler sem pressa.\n"
        f"- Perguntar à criança o que sentiu.\n"
        f"- Reforçar a frase final: {final_phrase}\n"
    )

    return {
        "id": str(uuid4()),
        "title": f"Guia - {story_title}",
        "content": content
    }
