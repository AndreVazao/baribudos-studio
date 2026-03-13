from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

SUPPORTED_LANGUAGES = [
    "pt-PT",
    "pt-BR",
    "en",
    "es",
    "fr",
    "de",
    "it",
    "nl",
    "zh",
    "ja",
]


def get_supported_languages() -> List[str]:
    return SUPPORTED_LANGUAGES


def _translate_text_free(text: str, target_language: str) -> str:
    if target_language == "pt-PT":
        return text
    return f"[{target_language}] {text}"


def translate_story(story: Dict[str, Any], target_language: str) -> Dict[str, Any]:
    pages = story.get("pages", []) or []

    translated_pages = []
    for page in pages:
        translated_pages.append({
            **page,
            "id": str(uuid4()),
            "text": _translate_text_free(str(page.get("text", "")).strip(), target_language)
        })

    return {
        **story,
        "id": str(uuid4()),
        "language": target_language,
        "pages": translated_pages
    }


def build_language_versions(story: Dict[str, Any], languages: List[str]) -> Dict[str, Dict[str, Any]]:
    target_languages = languages or [story.get("language", "pt-PT")]
    versions: Dict[str, Dict[str, Any]] = {}

    for language in target_languages:
        versions[language] = translate_story(story, language)

    return versions
