from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(project_root)

    host = os.getenv("BARIBUDOS_HOST", "0.0.0.0")
    port = int(os.getenv("BARIBUDOS_PORT", "8787"))
    reload_enabled = os.getenv("BARIBUDOS_RELOAD", "0").strip() == "1"

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    uvicorn.run(
        "studio_core.api.main:app",
        host=host,
        port=port,
        reload=reload_enabled,
        workers=1,
    )


if __name__ == "__main__":
    main()
