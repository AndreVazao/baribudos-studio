import subprocess
import os
from pathlib import Path

RUNTIME_DIR = Path("ai_runtime")

def ensure_runtime():
    RUNTIME_DIR.mkdir(exist_ok=True)

def start_stable_diffusion():
    path = RUNTIME_DIR / "stable_diffusion"

    if not path.exists():
        print("⚠ Stable Diffusion não instalado ainda")
        return

    subprocess.Popen(
        ["python", "launch.py"],
        cwd=str(path)
    )

def start_whisper():
    subprocess.Popen(["python", "-m", "whisper"])

def start_tts():
    subprocess.Popen(["python", "-m", "tts"])

def start_all():
    ensure_runtime()
    start_stable_diffusion()
    start_whisper()
    start_tts()
