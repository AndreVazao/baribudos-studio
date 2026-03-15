@echo off
set ROOT_DIR=%~dp0..
cd /d "%ROOT_DIR%"

start cmd /k "python deploy\start-backend.py"
start cmd /k "cd /d client\mobile-app && npm install && npm run dev"
