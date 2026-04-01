@echo off
REM wheel.bat – Build the xmlcompare Python wheel
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo === xmlcompare Python wheel build ===

REM Create virtual environment if it does not already exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing build tools...
pip install --quiet --upgrade pip build wheel

echo Cleaning previous dist...
if exist "dist" rd /s /q dist
if exist "xmlcompare.egg-info" rd /s /q xmlcompare.egg-info

echo Building wheel...
python -m build --wheel

echo.
echo Wheel files:
dir /b dist\*.whl

echo.
echo Done. Wheel is in the dist\ folder.
