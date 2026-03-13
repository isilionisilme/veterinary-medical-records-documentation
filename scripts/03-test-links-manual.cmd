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

echo [INFO] Running manual links test...
python -m unittest tests.test_docs_contracts.DocsContractsTest.test_links_resolve_to_existing_repository_files
if errorlevel 1 (
  echo [FAIL] Links test failed.
  set "EXIT_CODE=1"
  goto :end
)

echo [OK] Links test passed.
set "EXIT_CODE=0"

:end
echo.
pause
exit /b %EXIT_CODE%
