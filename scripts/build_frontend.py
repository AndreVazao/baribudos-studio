from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(cmd, cwd=cwd, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    frontend = root / "client" / "mobile-app"

    run(["npm", "install"], cwd=frontend)
    run(["npm", "run", "build"], cwd=frontend)

    print("Frontend compilado com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
