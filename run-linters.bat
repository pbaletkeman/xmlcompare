@echo off
REM
REM Windows Batch script to run all linters
REM Runs ruff for Python and checkstyle for Java
REM

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo Running Linters
echo ============================================================
echo.

set LINTER_FAILED=0

REM Python ruff linter
echo [1/2] Running Python linter (ruff)...
echo.
cd python
python -m ruff check . --no-cache
if errorlevel 1 (
    echo ERROR: Python linter found issues
    set LINTER_FAILED=1
) else (
    echo SUCCESS: Python linting passed
)
cd ..
echo.

REM Java checkstyle linter
echo [2/2] Running Java linter (checkstyle)...
echo.
cd java
call mvn checkstyle:check -q
if errorlevel 1 (
    echo ERROR: Java linter found issues
    set LINTER_FAILED=1
) else (
    echo SUCCESS: Java linting passed
)
cd ..
echo.

REM Summary
echo ============================================================
if %LINTER_FAILED% == 0 (
    echo All linters passed ^!
    echo ============================================================
    exit /b 0
) else (
    echo Some linters reported issues. See above for details.
    echo ============================================================
    exit /b 1
)
