from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

RUNTIME_DIR = Path("ai_runtime")

def _log(msg: str):
    print(f"[AI_RUNTIME] {msg}")

def ensure_runtime():
    RUNTIME_DIR.mkdir(exist_ok=True)

def _is_process_running(name: str) -> bool:
    try:
        import psutil
        for p in psutil.process_iter(["name", "cmdline"]):
            if name.lower() in " ".join(p.info.get("cmdline") or []).lower():
                return True
    except:
        pass
    return False

def start_stable_diffusion():
    path = RUNTIME_DIR / "stable_diffusion"

    if not path.exists():
        _log("Stable Diffusion não instalado")
        return

    if _is_process_running("launch.py"):
        _log("Stable Diffusion já em execução")
        return

    _log("A iniciar Stable Diffusion...")
    subprocess.Popen(
        [sys.executable, "launch.py"],
        cwd=str(path),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def start_whisper():
    if _is_process_running("whisper"):
        _log("Whisper já em execução")
        return

    _log("A iniciar Whisper...")
    subprocess.Popen(
        [sys.executable, "-m", "whisper"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def start_tts():
    if _is_process_running("tts"):
        _log("TTS já em execução")
        return

    _log("A iniciar TTS...")
    subprocess.Popen(
        [sys.executable, "-m", "tts"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def start_all():
    _log("Bootstrap IA iniciado")
    ensure_runtime()

    start_stable_diffusion()
    time.sleep(2)

    start_whisper()
    time.sleep(1)

    start_tts()

    _log("Bootstrap IA concluído")
