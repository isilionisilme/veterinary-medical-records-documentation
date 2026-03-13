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

echo [INFO] Running build-only test...
python -m unittest tests.test_docs_contracts.DocsContractsTest.test_sync_and_mkdocs_build
if errorlevel 1 (
  echo [FAIL] Build-only test failed.
  set "EXIT_CODE=1"
  goto :end
)

echo [OK] Build-only test passed.
set "EXIT_CODE=0"

:end
echo.
pause
exit /b %EXIT_CODE%
