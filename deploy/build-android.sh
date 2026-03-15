#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$ROOT_DIR/client/mobile-app"

cd "$APP_DIR"

npm install
npm run build
npx cap sync android

echo ""
echo "Android sync concluído."
echo "Abre o Android Studio com:"
echo "npx cap open android"
