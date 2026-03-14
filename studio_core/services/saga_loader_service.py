from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from studio_core.core.config import resolve_project_path


def _studio_sagas_root() -> Path:
    return resolve_project_path("studio", "sagas")


def _load_json(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_saga(saga_id: str) -> Dict[str, Any]:
    saga_path = _studio_sagas_root() / saga_id

    if not saga_path.exists():
        raise FileNotFoundError(f"Saga não encontrada: {saga_id}")

    return {
        "id": saga_id,
        "visual_canon": _load_json(saga_path / "visual-canon.json"),
        "narrative_canon": _load_json(saga_path / "narrative-canon.json"),
        "characters_master": _load_json(saga_path / "characters-master.json"),
        "episode_canon": _load_json(saga_path / "episode-canon.json"),
        "series_arc_canon": _load_json(saga_path / "series-arc-canon.json"),
        "pedagogical_canon": _load_json(saga_path / "pedagogical-canon.json"),
        "age_badge_canon": _load_json(saga_path / "age-badge-canon.json"),
    }


def list_sagas_from_studio() -> list[str]:
    root = _studio_sagas_root()
    if not root.exists():
      return []
    return sorted([item.name for item in root.iterdir() if item.is_dir()])


def is_protected_ip(saga_id: str) -> bool:
    return saga_id == "baribudos"


def can_user_edit_saga(user_role: str, saga_id: str) -> bool:
    if is_protected_ip(saga_id):
        return user_role in {"creator", "owner"}
    return True


def validate_story_structure(saga_id: str, story_structure: list[str]) -> dict:
    saga = load_saga(saga_id)
    canon = saga.get("narrative_canon") or {}
    expected = canon.get("narrative_structure_standard", [])
    missing = [step for step in expected if step not in story_structure]

    return {
        "ok": len(missing) == 0,
        "expected": expected,
        "received": story_structure,
        "missing": missing,
    }


def validate_visual_meta(saga_id: str, illustration_meta: dict) -> dict:
    load_saga(saga_id)

    violations = []

    if bool(illustration_meta.get("realistic")):
        violations.append("realism_not_allowed")

    if bool(illustration_meta.get("scary")):
        violations.append("scary_not_allowed")

    return {
        "ok": len(violations) == 0,
        "violations": violations,
  }
