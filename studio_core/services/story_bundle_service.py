from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid5, NAMESPACE_URL

BUNDLE_SIZE = 5


def _text(value: Any) -> str:
    return str(value or "").strip()


def _approved(story: Dict[str, Any]) -> bool:
    """Accept only explicit approval signals; truthy strings are never approvals."""
    return (
        story.get("approved") is True
        or _text(story.get("editorial_status")).lower() == "approved"
        or _text(story.get("approval_state")).lower() == "approved"
    )


def _identity(story: Dict[str, Any]) -> tuple[str, str, str]:
    ip_slug = _text(story.get("ip_slug"))
    saga_slug = _text(story.get("saga_slug"))
    language = _text(story.get("language"))
    if not ip_slug or not saga_slug or not language:
        raise ValueError("approved_story_requires_ip_saga_and_language")
    return ip_slug, saga_slug, language


def _validate_bundle_members(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    stories = bundle.get("stories")
    if not isinstance(stories, list) or len(stories) != BUNDLE_SIZE:
        raise ValueError("bundle_requires_exactly_five_stories")
    if any(not isinstance(item, dict) or not _approved(item) for item in stories):
        raise ValueError("bundle_requires_five_explicitly_approved_stories")

    ids = [_text(item.get("id")) for item in stories]
    if any(not item_id for item_id in ids):
        raise ValueError("bundle_requires_stable_story_ids")
    if len(set(ids)) != BUNDLE_SIZE:
        raise ValueError("bundle_requires_five_distinct_story_ids")

    identities = {_identity(item) for item in stories}
    if len(identities) != 1:
        raise ValueError("bundle_cannot_mix_ip_saga_or_language")
    expected = _identity({
        "ip_slug": bundle.get("ip_slug"),
        "saga_slug": bundle.get("saga_slug"),
        "language": bundle.get("language"),
    })
    if identities != {expected}:
        raise ValueError("bundle_identity_does_not_match_story_members")
    return stories


def _sequence_key(story: Dict[str, Any]) -> tuple:
    sequence = story.get("sequence_number")
    try:
        sequence_value = int(sequence)
    except (TypeError, ValueError):
        sequence_value = 2**31 - 1
    return (sequence_value, _text(story.get("created_at")), _text(story.get("id")))


def select_complete_story_groups(
    stories: Iterable[Dict[str, Any]],
    *,
    bundle_size: int = BUNDLE_SIZE,
) -> List[Dict[str, Any]]:
    """Select deterministic groups keyed by IP, saga and locale.

    Only explicit approvals with stable, distinct IDs and complete editorial
    identity are eligible. Incomplete groups remain available for a later run.
    """
    if bundle_size != BUNDLE_SIZE:
        raise ValueError("five_story_bundle_size_is_fixed")
    grouped: Dict[tuple[str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for story in stories:
        if not isinstance(story, dict) or not _approved(story):
            continue
        if not _text(story.get("id")):
            continue
        identity = _identity(story)
        grouped[identity].append(story)

    result: List[Dict[str, Any]] = []
    for (ip_slug, saga_slug, language), candidates in sorted(grouped.items()):
        ordered = sorted(candidates, key=_sequence_key)
        seen_ids: set[str] = set()
        unique: List[Dict[str, Any]] = []
        for item in ordered:
            story_id = _text(item.get("id"))
            if story_id in seen_ids:
                raise ValueError(f"duplicate_story_id_in_editorial_group:{story_id}")
            seen_ids.add(story_id)
            unique.append(item)
        for offset in range(0, len(unique) - BUNDLE_SIZE + 1, BUNDLE_SIZE):
            members = unique[offset : offset + BUNDLE_SIZE]
            ids = [_text(item.get("id")) for item in members]
            identity_key = f"{ip_slug}|{saga_slug}|{language}|{'|'.join(ids)}"
            result.append({
                "id": str(uuid5(NAMESPACE_URL, identity_key)),
                "ip_slug": ip_slug,
                "saga_slug": saga_slug,
                "language": language,
                "story_ids": ids,
                "stories": members,
                "story_count": len(members),
                "bundle_size": BUNDLE_SIZE,
                "status": "ready_for_bundle",
            })
    return result


def build_parent_guide(bundle: Dict[str, Any], *, output_path: str | Path) -> Dict[str, Any]:
    stories = _validate_bundle_members(bundle)
    title = _text(bundle.get("title")) or "Guia para Pais — cinco histórias"
    lines = [
        f"# {title}",
        "",
        f"**IP:** {_text(bundle.get('ip_slug'))}  ",
        f"**Saga:** {_text(bundle.get('saga_slug'))}  ",
        f"**Idioma:** {_text(bundle.get('language'))}  ",
        "**Conjunto:** cinco histórias aprovadas",
        "",
        "## Como utilizar este guia",
        "",
        "Leia ou ouça cada história com a criança, respeitando o seu ritmo. Não transforme a leitura num teste. Escute primeiro, acolha as emoções e adapte as perguntas à idade.",
        "",
        "## As cinco histórias",
        "",
    ]
    for index, story in enumerate(stories, start=1):
        story_title = _text(story.get("title")) or f"História {index}"
        theme = _text(story.get("value_theme") or story.get("theme")) or "Tema a conversar"
        lines.extend([
            f"### {index}. {story_title}",
            "",
            f"- **Tema:** {theme}",
            "- **Conversa:** O que aconteceu nesta história? Como se sentiu a personagem?",
            "- **Ligação ao dia a dia:** Já viveste uma situação em que precisaste de pedir ajuda?",
            "- **Ação do adulto:** Escutar sem julgar, validar sentimentos e reforçar que a criança pode procurar um adulto de confiança.",
            "",
        ])
    lines.extend([
        "## Conversa em família",
        "",
        "- Que personagem te fez sentir acompanhado?",
        "- Que escolhas ajudaram a resolver os problemas?",
        "- A quem podes pedir ajuda quando algo te deixa desconfortável ou inseguro?",
        "- Há alguma coisa que gostasses de voltar a conversar com um adulto de confiança?",
        "",
        "## Nota de segurança",
        "",
        "A criança não é responsável por resolver situações perigosas sozinha. Deve procurar um adulto de confiança. Nenhuma história deve incentivar confronto, segredo perigoso ou culpabilização da criança.",
        "",
        "## Registo familiar",
        "",
        "Use este espaço para anotar perguntas, descobertas e temas que mereçam nova conversa, sem recolher dados pessoais desnecessários.",
        "",
    ])
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    return {
        "format": "markdown",
        "file_path": str(target),
        "story_count": BUNDLE_SIZE,
        "story_ids": [_text(item.get("id")) for item in stories],
        "title": title,
        "status": "generated",
    }


def _approved_clip_path(story: Dict[str, Any], language: str, storage_root: Path) -> Path:
    video_path = _text(story.get("mini_series_path"))
    if not video_path:
        outputs = story.get("outputs") if isinstance(story.get("outputs"), dict) else {}
        videos = outputs.get("video") if isinstance(outputs.get("video"), dict) else {}
        language_output = videos.get(language)
        if isinstance(language_output, dict):
            video_path = _text(language_output.get("file_path"))
    if not video_path:
        raise ValueError(f"mini_series_asset_missing:{_text(story.get('id'))}")

    candidate = Path(video_path)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(storage_root)
    except (OSError, ValueError):
        raise ValueError(f"mini_series_asset_outside_approved_storage:{_text(story.get('id'))}") from None
    if not resolved.is_file() or resolved.stat().st_size == 0:
        raise ValueError(f"mini_series_asset_missing:{_text(story.get('id'))}")
    return resolved


def build_five_story_compilation(
    bundle: Dict[str, Any],
    *,
    output_path: str | Path,
    storage_root: str | Path,
) -> Dict[str, Any]:
    stories = _validate_bundle_members(bundle)
    root = Path(storage_root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("approved_storage_root_must_be_directory")
    clips = [_approved_clip_path(story, _text(bundle["language"]), root) for story in stories]

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("ffmpeg_and_ffprobe_are_required")

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_target = target.with_name(f".{target.stem}.tmp{target.suffix or '.mp4'}")
    try:
        with tempfile.TemporaryDirectory(prefix="baribudos-five-story-") as temp_dir:
            concat_file = Path(temp_dir) / "concat.txt"
            entries = []
            for clip in clips:
                escaped = clip.as_posix().replace("'", "'\\''")
                entries.append(f"file '{escaped}'")
            concat_file.write_text("\n".join(entries) + "\n", encoding="utf-8")
            subprocess.run(
                [
                    ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "concat", "-safe", "0", "-i", str(concat_file),
                    "-map", "0:v:0", "-map", "0:a:0?",
                    "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-movflags", "+faststart", str(temporary_target),
                ],
                check=True,
                timeout=900,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        probe = subprocess.run(
            [
                ffprobe, "-v", "error", "-show_entries",
                "format=duration,size:stream=codec_type,codec_name",
                "-of", "json", str(temporary_target),
            ],
            check=True,
            timeout=30,
            capture_output=True,
            text=True,
        )
        metadata = json.loads(probe.stdout)
        streams = metadata.get("streams", [])
        if not any(item.get("codec_type") == "video" for item in streams):
            raise RuntimeError("compilation_has_no_video_stream")
        if not any(item.get("codec_type") == "audio" for item in streams):
            raise RuntimeError("compilation_has_no_audio_stream")
        os.replace(temporary_target, target)
    finally:
        temporary_target.unlink(missing_ok=True)

    return {
        "format": "mp4",
        "file_path": str(target),
        "story_count": BUNDLE_SIZE,
        "story_ids": [_text(item.get("id")) for item in stories],
        "duration_seconds": float(metadata.get("format", {}).get("duration", 0)),
        "size_bytes": target.stat().st_size,
        "video_codec": next(item.get("codec_name") for item in streams if item.get("codec_type") == "video"),
        "audio_codec": next(item.get("codec_name") for item in streams if item.get("codec_type") == "audio"),
        "status": "generated",
    }


def build_five_story_bundle(
    stories: Iterable[Dict[str, Any]],
    *,
    output_dir: str | Path,
    storage_root: str | Path,
    title: str = "",
    bundle_id: str = "",
) -> Dict[str, Any]:
    groups = select_complete_story_groups(stories)
    if not groups:
        return {"status": "waiting_for_five_approved_stories", "bundles_created": 0}
    if bundle_id:
        selected = [item for item in groups if item["id"] == bundle_id]
        if not selected:
            raise ValueError("selected_story_bundle_not_found")
        bundle = selected[0]
    elif len(groups) == 1:
        bundle = groups[0]
    else:
        raise ValueError("multiple_complete_groups_require_bundle_id")
    bundle["title"] = title or "Guia para Pais e Filme — cinco histórias"
    root = Path(output_dir)
    guide = build_parent_guide(bundle, output_path=root / "parents-guide.md")
    compilation = build_five_story_compilation(
        bundle,
        output_path=root / "five-story-mini-film.mp4",
        storage_root=storage_root,
    )
    return {
        "id": bundle["id"],
        "status": "completed",
        "story_ids": bundle["story_ids"],
        "story_count": BUNDLE_SIZE,
        "guide": guide,
        "compilation": compilation,
    }
