@echo off
REM build.bat – Set up virtual environment, install dependencies, and run tests
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo === xmlcompare Python build ===

REM Create virtual environment if it does not already exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install --quiet -r requirements.txt
pip install --quiet pytest-cov

echo Running tests...
pytest tests/ -v --cov=xmlcompare --cov-report=term-missing

if %ERRORLEVEL% NEQ 0 (
    echo Tests failed.
    exit /b %ERRORLEVEL%
)

echo Build complete.
endlocal
