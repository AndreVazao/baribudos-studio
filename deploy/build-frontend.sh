#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$ROOT_DIR/client/mobile-app"

cd "$APP_DIR"
npm install
npm run build

echo ""
echo "Frontend build concluído em:"
echo "$APP_DIR/dist"
