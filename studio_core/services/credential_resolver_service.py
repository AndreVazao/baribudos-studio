from __future__ import annotations

import os
from typing import Any, Iterable, List

from studio_core.core.storage import list_json_items

SECRETS_VAULTS_FILE = "data/secret_vaults.json"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _iter_vault_entries(target: str | None = None, environment: str | None = None):
    vaults = list_json_items(SECRETS_VAULTS_FILE)
    target_value = _normalize_text(target).lower()
    environment_value = _normalize_text(environment).lower()

    prioritized = []
    fallback = []

    for vault in reversed(vaults):
        vault_target = _normalize_text(vault.get("target")).lower()
        vault_environment = _normalize_text(vault.get("environment")).lower()

        matches_target = not target_value or vault_target == target_value
        matches_environment = not environment_value or vault_environment == environment_value

        collection = prioritized if matches_target and matches_environment else fallback
        collection.append(vault)

    for vault in prioritized + fallback:
        for row in _safe_list(vault.get("rows")):
            if _normalize_text(row.get("kind")) == "entry":
                yield row


def resolve_credential(
    env_name: str,
    *,
    target: str | None = None,
    environment: str | None = None,
    aliases: Iterable[str] | None = None,
    default: str = "",
) -> str:
    names = [_normalize_text(env_name)]
    names.extend(_normalize_text(alias) for alias in (aliases or []) if _normalize_text(alias))
    names = [name for name in names if name]

    for name in names:
        env_value = _normalize_text(os.getenv(name))
        if env_value:
            return env_value

    candidate_keys = {name.lower() for name in names}
    for row in _iter_vault_entries(target=target, environment=environment):
        key = _normalize_text(row.get("key")).lower()
        if key in candidate_keys:
            value = _normalize_text(row.get("value"))
            if value:
                return value

    return _normalize_text(default)
