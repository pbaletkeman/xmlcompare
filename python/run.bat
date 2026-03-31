@echo off
REM run.bat – Activate the virtual environment and run xmlcompare with any
REM            arguments passed to this script.
REM
REM Usage:
REM   run.bat --files samples\orders_expected.xml samples\orders_actual_diff.xml
REM   run.bat --dirs samples\ samples\ --summary
REM   run.bat --help

cd /d "%~dp0"

if not exist ".venv" (
    echo Virtual environment not found. Run build.bat first. 1>&2
    exit /b 1
)

call .venv\Scripts\activate.bat
python xmlcompare.py %*
exit /b %ERRORLEVEL%
