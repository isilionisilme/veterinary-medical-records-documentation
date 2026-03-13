@echo off
setlocal

cd /d "%~dp0.."

echo [INFO] Repo root: %CD%
echo [INFO] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
  echo [FAIL] Python is not available in PATH.
  echo [HINT] Install Python and ensure "python" works from terminal.
  set "EXIT_CODE=1"
  goto :end
)

echo [INFO] Checking MkDocs...
mkdocs --version >nul 2>&1
if errorlevel 1 (
  echo [FAIL] MkDocs is not available in PATH.
  echo [HINT] Run: pip install mkdocs-material==9.*
  set "EXIT_CODE=1"
  goto :end
)

echo [INFO] Syncing docs source to .mkdocs...
python scripts/sync_mkdocs_docs.py
if errorlevel 1 (
  echo [FAIL] Sync step failed.
  set "EXIT_CODE=1"
  goto :end
)

echo [INFO] Running mkdocs build --clean...
mkdocs build --clean
if errorlevel 1 (
  echo [FAIL] Docs build failed.
  set "EXIT_CODE=1"
  goto :end
)

echo [OK] Docs build completed successfully.
set "EXIT_CODE=0"

:end
echo.
pause
exit /b %EXIT_CODE%
