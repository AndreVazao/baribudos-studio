@echo off
set ROOT_DIR=%~dp0..
cd /d "%ROOT_DIR%"

python deploy\smoke_test.py
