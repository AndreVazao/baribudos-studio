#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$ROOT_DIR/client/mobile-app"

cd "$APP_DIR"
npm install

if [ ! -d "src-tauri" ]; then
  echo "src-tauri não encontrado."
  exit 1
fi

echo "Tauri base já presente."
