#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 deploy/start-backend.py &
BACKEND_PID=$!

cd client/mobile-app
npm install
npm run dev

kill $BACKEND_PID
