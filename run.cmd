@echo off
setlocal enabledelayedexpansion

REM ===== Sticker Factory one-shot runner (Windows CMD) =====
cd /d "%~dp0"

echo [0] Working dir: %cd%

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating venv...
  python -m venv .venv
  if errorlevel 1 (
    echo Failed to create venv. Ensure Python is installed.
    pause
    exit /b 1
  )
)

echo [2/4] Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
  echo Failed to upgrade pip.
  pause
  exit /b 1
)

echo [3/4] Installing dependencies...
".venv\Scripts\pip.exe" install -r requirements.txt
if errorlevel 1 (
  echo Failed to install dependencies.
  pause
  exit /b 1
)

echo [4/4] Preparing sample images...
".venv\Scripts\python.exe" -m sticker_factory.samples

echo Starting Streamlit app...
set PYTHONPATH=%cd%
".venv\Scripts\streamlit.exe" run "sticker_factory\app.py" --server.port 8501

endlocal
