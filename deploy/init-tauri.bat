@echo off
set ROOT_DIR=%~dp0..
set APP_DIR=%ROOT_DIR%\client\mobile-app

cd /d "%APP_DIR%"
call npm install
if errorlevel 1 exit /b 1

if not exist "src-tauri" (
  echo src-tauri nao encontrado.
  exit /b 1
)

echo Tauri base ja presente.
