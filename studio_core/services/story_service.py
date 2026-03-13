from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4


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


def _build_default_story_text(payload: Dict[str, Any]) -> str:
    title = str(payload.get("title", "Nova História")).strip()
    saga_name = str(payload.get("saga_name", "Baribudos")).strip()
    value_theme = str(payload.get("value_theme", "coragem")).strip()
    protagonist = str(payload.get("protagonist", "Tilo")).strip()

    return (
        f"{protagonist} acordou cedo na floresta encantada de {saga_name}. "
        f"Nesse dia, uma pequena dúvida apareceu no seu coração. "
        f"Ele queria fazer o certo, mas ainda não sabia como. "
        f"Com calma, observou as árvores, escutou o vento e respirou fundo. "
        f"Pouco a pouco, percebeu que a verdadeira força nasce quando escolhemos o caminho seguro. "
        f"No final, {protagonist} aprendeu uma lição sobre {value_theme}, "
        f"e voltou para casa mais confiante, sereno e pronto para partilhar o que descobriu. "
        f"Assim terminou {title}, uma história que protege."
    )


def generate_story(payload: Dict[str, Any]) -> Dict[str, Any]:
    title = str(payload.get("title", "Nova História")).strip()
    language = str(payload.get("language", "pt-PT")).strip()

    raw_text = _normalize_text(
        payload.get("raw_text")
        or payload.get("input", {}).get("raw_text")
        or _build_default_story_text(payload)
    )

    pages = _split_story_into_pages(
        raw_text,
        max_words_per_page=int(payload.get("max_words_per_page", 35))
    )

    return {
        "id": str(uuid4()),
        "title": title,
        "language": language,
        "raw_text": raw_text,
        "pages": pages
    }


def generate_volume_guide(payload: Dict[str, Any]) -> Dict[str, Any]:
    project_title = str(payload.get("project_title", "Projeto")).strip()
    story = payload.get("story", {}) or {}
    story_title = str(story.get("title", project_title)).strip()
    page_count = len(story.get("pages", []) or [])

    content = (
        f"Guia do volume: {story_title}\n\n"
        f"Este volume foi preparado para leitura calma e partilhada.\n"
        f"Número de páginas: {page_count}\n"
        f"Objetivo emocional: promover conversa segura entre criança e família.\n\n"
        f"Sugestão de uso:\n"
        f"- Ler sem pressa.\n"
        f"- Perguntar à criança o que sentiu.\n"
        f"- Reforçar a moral prática no final.\n"
    )

    return {
        "id": str(uuid4()),
        "title": f"Guia - {story_title}",
        "content": content
  }
