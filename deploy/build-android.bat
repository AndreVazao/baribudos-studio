@echo off
set ROOT_DIR=%~dp0..
set APP_DIR=%ROOT_DIR%\client\mobile-app

cd /d "%APP_DIR%"
call npm install
if errorlevel 1 exit /b 1

call npm run build
if errorlevel 1 exit /b 1

call npx cap sync android
if errorlevel 1 exit /b 1

echo.
echo Android sync concluido.
echo Abre o Android Studio com:
echo npx cap open android
