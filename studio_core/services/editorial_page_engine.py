from __future__ import annotations

import re
from typing import Any, Dict, List
from uuid import uuid4


DEFAULT_CHILD_LINES = 4
DEFAULT_ADULT_LINES = 12


def _clean_text(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def _estimate_page_size(age_group: str | None, genre: str | None) -> int:
    if age_group:
        if any(x in age_group for x in ["3", "4", "5"]):
            return 3
        if any(x in age_group for x in ["6", "7"]):
            return 4
        if any(x in age_group for x in ["8", "9", "10"]):
            return 5

    if genre == "adult":
        return DEFAULT_ADULT_LINES

    return DEFAULT_CHILD_LINES


def _chunk_paragraph(paragraph: str, max_lines: int) -> List[str]:
    sentences = re.split(r"(?<=[.!?]) +", paragraph)
    pages: List[str] = []
    current: List[str] = []

    for sentence in sentences:
        current.append(sentence)
        if len(current) >= max_lines:
            pages.append(" ".join(current))
            current = []

    if current:
        pages.append(" ".join(current))

    return pages


def split_into_pages(
    text: str,
    age_group: str | None = None,
    genre: str | None = None,
) -> List[str]:
    text = _clean_text(text)
    paragraphs = _split_paragraphs(text)
    max_lines = _estimate_page_size(age_group, genre)

    pages: List[str] = []
    for paragraph in paragraphs:
        pages.extend(_chunk_paragraph(paragraph, max_lines))

    return pages


def build_editorial_pages(
    text: str,
    metadata: Dict[str, Any],
) -> List[Dict[str, Any]]:
    pages_raw = split_into_pages(
        text,
        metadata.get("age_group"),
        metadata.get("genre"),
    )

    pages: List[Dict[str, Any]] = []
    for index, page_text in enumerate(pages_raw, start=1):
        pages.append(
            {
                "id": str(uuid4()),
                "page_number": index,
                "text": page_text,
                "illustration": None,
                "audio": None,
                "locked": False,
            }
        )

    return pages


def enrich_pages_with_editorial_intelligence(
    pages: List[Dict[str, Any]],
    metadata: Dict[str, Any],
) -> List[Dict[str, Any]]:
    theme = str(metadata.get("theme", "") or "").strip()
    moral = str(metadata.get("moral", "") or "").strip()
    pedagogical_goal = str(metadata.get("pedagogical_goal", "") or "").strip()
    target_language = str(metadata.get("language", "pt-PT") or "pt-PT").strip()

    enriched: List[Dict[str, Any]] = []

    for index, page in enumerate(pages, start=1):
        text = str(page.get("text", "") or "").strip()

        enriched.append(
            {
                **page,
                "page_number": index,
                "language": target_language,
                "theme": theme,
                "moral": moral,
                "pedagogical_goal": pedagogical_goal,
                "reading_level": metadata.get("age_group", ""),
                "editorial_flags": {
                    "needs_illustration": index == 1 or len(text) < 260,
                    "is_opening_page": index == 1,
                    "is_closing_page": index == len(pages),
                    "is_dialogue_heavy": ":" in text,
                },
            }
        )

    return enriched


def apply_ip_canon_to_pages(
    pages: List[Dict[str, Any]],
    ip_runtime: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    ip_runtime = ip_runtime or {}

    ip_name = str(ip_runtime.get("name", "") or "").strip()
    palette = ip_runtime.get("palette", {}) or {}
    metadata = ip_runtime.get("metadata", {}) or {}
    canons = ip_runtime.get("canons", {}) or {}

    visual = canons.get("visual", {}) or {}
    narrative = canons.get("narrative", {}) or {}
    pedagogical = canons.get("pedagogical", {}) or {}

    visual_style = str(visual.get("style", "") or "").strip()
    world_rules = visual.get("environment_rules", {}) or {}
    world_name = str(world_rules.get("world", "") or "").strip()

    emotional_tone = visual.get("emotional_tone", []) or []
    if not isinstance(emotional_tone, list):
        emotional_tone = []

    story_values = pedagogical.get("values", []) or []
    if not isinstance(story_values, list):
        story_values = []

    enriched: List[Dict[str, Any]] = []

    for page in pages:
        text = str(page.get("text", "") or "").strip()

        illustration_prompt_base = ", ".join(
            [
                part
                for part in [
                    ip_name,
                    visual_style,
                    world_name,
                    ", ".join([str(x).strip() for x in emotional_tone if str(x).strip()]),
                    str(metadata.get("target_age", "") or "").strip(),
                ]
                if part
            ]
        )

        enriched.append(
            {
                **page,
                "ip_context": {
                    "ip_name": ip_name,
                    "series_name": str(metadata.get("series_name", "") or "").strip(),
                    "target_age": str(metadata.get("target_age", "") or "").strip(),
                    "genre": str(metadata.get("genre", "") or "").strip(),
                    "palette": palette,
                    "visual_style": visual_style,
                    "world_name": world_name,
                    "story_values": story_values,
                    "narrative_rules": narrative,
                },
                "illustration_brief": {
                    "prompt_base": illustration_prompt_base,
                    "page_excerpt": text[:300],
                    "needs_illustration": bool(
                        (page.get("editorial_flags", {}) or {}).get("needs_illustration", False)
                    ),
                },
            }
        )

    return enriched


def build_editorial_package(
    text: str,
    metadata: Dict[str, Any],
    ip_runtime: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    base_pages = build_editorial_pages(text, metadata)
    editorial_pages = enrich_pages_with_editorial_intelligence(base_pages, metadata)
    final_pages = apply_ip_canon_to_pages(editorial_pages, ip_runtime=ip_runtime)

    return {
        "ok": True,
        "metadata": metadata,
        "pages": final_pages,
        "pages_count": len(final_pages),
    }


def repaginate_existing_pages(
    pages: List[Dict[str, Any]],
    metadata: Dict[str, Any],
) -> List[Dict[str, Any]]:
    full_text = "\n\n".join(
        str(page.get("text", "") or "").strip()
        for page in pages
        if str(page.get("text", "") or "").strip()
    ).strip()

    return build_editorial_pages(full_text, metadata)


def merge_two_pages(
    pages: List[Dict[str, Any]],
    first_page_number: int,
    second_page_number: int,
) -> List[Dict[str, Any]]:
    normalized = sorted([int(first_page_number), int(second_page_number)])
    first_num, second_num = normalized[0], normalized[1]

    first_page = None
    second_page = None
    remaining: List[Dict[str, Any]] = []

    for page in pages:
        current_number = int(page.get("page_number", 0) or 0)
        if current_number == first_num:
            first_page = page
            continue
        if current_number == second_num:
            second_page = page
            continue
        remaining.append(page)

    if not first_page or not second_page:
        return pages

    merged_text = "\n\n".join(
        [
            str(first_page.get("text", "") or "").strip(),
            str(second_page.get("text", "") or "").strip(),
        ]
    ).strip()

    merged_page = {
        **first_page,
        "id": str(uuid4()),
        "text": merged_text,
        "locked": False,
    }

    rebuilt = remaining + [merged_page]
    rebuilt = sorted(rebuilt, key=lambda item: int(item.get("page_number", 999999) or 999999))

    final_pages: List[Dict[str, Any]] = []
    for idx, page in enumerate(rebuilt, start=1):
        final_pages.append(
            {
                **page,
                "page_number": idx,
            }
        )

    return final_pages


def split_one_page(
    pages: List[Dict[str, Any]],
    page_number: int,
    age_group: str | None = None,
    genre: str | None = None,
) -> List[Dict[str, Any]]:
    target = None
    remaining: List[Dict[str, Any]] = []

    for page in pages:
        current_number = int(page.get("page_number", 0) or 0)
        if current_number == int(page_number):
            target = page
            continue
        remaining.append(page)

    if not target:
        return pages

    split_pages = split_into_pages(
        str(target.get("text", "") or "").strip(),
        age_group=age_group,
        genre=genre,
    )

    if len(split_pages) <= 1:
        return pages

    new_pages: List[Dict[str, Any]] = []
    for chunk in split_pages:
        new_pages.append(
            {
                **target,
                "id": str(uuid4()),
                "text": chunk,
                "locked": False,
            }
        )

    rebuilt = remaining + new_pages
    rebuilt = sorted(rebuilt, key=lambda item: int(item.get("page_number", 999999) or 999999))

    final_pages: List[Dict[str, Any]] = []
    for idx, page in enumerate(rebuilt, start=1):
        final_pages.append(
            {
                **page,
                "page_number": idx,
            }
        )

    return final_pages


def assign_visual_slots(
    pages: List[Dict[str, Any]],
    illustration_every: int = 2,
) -> List[Dict[str, Any]]:
    illustration_every = max(1, int(illustration_every or 1))
    result: List[Dict[str, Any]] = []

    for idx, page in enumerate(pages, start=1):
        flags = page.get("editorial_flags", {}) or {}
        needs_illustration = bool(flags.get("needs_illustration", False)) or idx % illustration_every == 1

        result.append(
            {
                **page,
                "editorial_flags": {
                    **flags,
                    "needs_illustration": needs_illustration,
                },
            }
        )

    return result


def build_book_preview_model(
    text: str,
    metadata: Dict[str, Any],
    ip_runtime: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    package = build_editorial_package(text, metadata, ip_runtime=ip_runtime)
    pages = assign_visual_slots(
        package.get("pages", []),
        illustration_every=int(metadata.get("illustration_every", 2) or 2),
    )

    preview_pages: List[Dict[str, Any]] = []
    for page in pages:
        preview_pages.append(
            {
                "id": page.get("id"),
                "page_number": page.get("page_number"),
                "title": f"Página {page.get('page_number')}",
                "text": page.get("text", ""),
                "layout": {
                    "show_illustration_slot": bool(
                        (page.get("editorial_flags", {}) or {}).get("needs_illustration", False)
                    ),
                    "show_badge": page.get("page_number") == 1,
                    "show_series_logo": page.get("page_number") == 1,
                },
                "illustration_brief": page.get("illustration_brief", {}),
            }
        )

    return {
        "ok": True,
        "metadata": metadata,
        "pages_count": len(preview_pages),
        "pages": preview_pages,
}
