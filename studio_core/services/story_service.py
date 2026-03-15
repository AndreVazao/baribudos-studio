from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from studio_core.services.story_generation_engine import generate_canon_story
from studio_core.services.saga_runtime_service import load_saga_runtime


def generate_story(payload: Dict[str, Any]) -> Dict[str, Any]:
    return generate_canon_story(payload)


def generate_volume_guide(payload: Dict[str, Any]) -> Dict[str, Any]:
    project_title = str(payload.get("project_title", "Projeto")).strip()
    story = payload.get("story", {}) or {}
    story_title = str(story.get("title", project_title)).strip()
    page_count = len(story.get("pages", []) or [])
    saga_id = str(story.get("saga_id", "baribudos")).strip()

    runtime = load_saga_runtime(saga_id)
    resolved = runtime.get("resolved", {}) or {}

    final_phrase = str(story.get("final_phrase") or resolved.get("final_phrase_rule") or "Na dúvida, escolhe o caminho seguro.").strip()
    mission = str(story.get("mission") or resolved.get("mission") or "").strip()
    target_age = str(story.get("target_age") or resolved.get("target_age") or "").strip()
    value_theme = str(story.get("value_theme") or "").strip()
    protagonist = str(story.get("protagonist") or "").strip()

    content = (
        f"Guia do volume: {story_title}\n\n"
        f"Série: {resolved.get('series_name') or runtime.get('name') or '-'}\n"
        f"Missão: {mission}\n"
        f"Faixa etária alvo: {target_age}\n"
        f"Protagonista: {protagonist or '-'}\n"
        f"Valor central: {value_theme or '-'}\n"
        f"Número de páginas: {page_count}\n\n"
        f"Sugestão de uso:\n"
        f"- Ler sem pressa.\n"
        f"- Perguntar à criança o que sentiu.\n"
        f"- Relacionar a história com escolhas seguras.\n"
        f"- Reforçar a frase final: {final_phrase}\n"
    )

    return {
        "id": str(uuid4()),
        "title": f"Guia - {story_title}",
        "content": content
    }
