from __future__ import annotations

import shutil
import sys
from pathlib import Path


def check_command(name: str) -> bool:
    return shutil.which(name) is not None


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent

    checks = {
        "python": True,
        "ffmpeg": check_command("ffmpeg"),
        "espeak": check_command("espeak") or check_command("espeak-ng"),
        "node": check_command("node"),
        "npm": check_command("npm"),
    }

    print("=== BARIBUDOS STUDIO RUNTIME CHECK ===")
    print(f"project_root: {project_root}")
    for key, value in checks.items():
        print(f"{key}: {'OK' if value else 'FALTA'}")

    failed = [key for key, value in checks.items() if not value]
    if failed:
        print("")
        print("Faltam dependências:", ", ".join(failed))
        return 1

    print("")
    print("Runtime validado com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
  
