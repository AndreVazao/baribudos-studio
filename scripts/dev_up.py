from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    frontend = root / "client" / "mobile-app"

    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "studio_core.api.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8787",
        "--reload",
    ]

    frontend_install = subprocess.run(["npm", "install"], cwd=frontend, check=False)
    if frontend_install.returncode != 0:
        return frontend_install.returncode

    backend = subprocess.Popen(backend_cmd, cwd=root)
    time.sleep(2)
    frontend_proc = subprocess.Popen(["npm", "run", "dev"], cwd=frontend)

    try:
        return frontend_proc.wait()
    finally:
        backend.terminate()
        try:
            backend.wait(timeout=5)
        except Exception:
            backend.kill()


if __name__ == "__main__":
    raise SystemExit(main())
