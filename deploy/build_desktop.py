import os
import subprocess
import sys

APP_NAME = "BaribudosStudio"

def build():
    print("🔨 Building Desktop EXE...")

    subprocess.run([
        sys.executable,
        "-m",
        "PyInstaller",
        "main.py",
        "--onefile",
        "--noconsole",
        "--name",
        APP_NAME,
        "--add-data",
        "studio;studio",
        "--add-data",
        "public;public",
        "--add-data",
        "storage;storage"
    ])

    print("✅ Desktop build complete")


if __name__ == "__main__":
    build()
