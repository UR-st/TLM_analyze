@echo off
cd /d %~dp0
setlocal

rem Create venv if missing (avoids admin rights and keeps deps local)
if not exist ".venv\\Scripts\\python.exe" (
  echo [setup] Creating virtual environment: .venv
  python -m venv .venv
  if errorlevel 1 (
    echo [error] Failed to create venv. Make sure Python is installed and on PATH.
    exit /b 1
  )
)

rem Ensure deps (pip will skip already satisfied)
echo [setup] Installing requirements (if needed)
".venv\\Scripts\\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo [error] pip install failed.
  exit /b 1
)

rem Run
".venv\\Scripts\\python.exe" src\\main.py
pause
