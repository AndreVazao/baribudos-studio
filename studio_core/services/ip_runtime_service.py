from __future__ import annotations

from typing import Any, Dict

from studio_core.services.saga_runtime_service import load_saga_runtime


def load_ip_runtime(slug: str) -> Dict[str, Any]:
    return load_saga_runtime(slug)
