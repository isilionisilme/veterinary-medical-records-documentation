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

echo [INFO] Running full docs contracts suite...
python -m unittest tests.test_docs_contracts
if errorlevel 1 (
  echo [FAIL] Full docs contracts suite failed.
  set "EXIT_CODE=1"
  goto :end
)

echo [OK] Full docs contracts suite passed.
set "EXIT_CODE=0"

:end
echo.
pause
exit /b %EXIT_CODE%
