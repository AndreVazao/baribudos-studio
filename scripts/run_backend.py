from __future__ import annotations

import subprocess
import sys


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "studio_core.api.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8787",
    ]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
