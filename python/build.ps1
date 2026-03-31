# build.ps1 – Set up virtual environment, install dependencies, and run tests
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=== xmlcompare Python build ===" -ForegroundColor Cyan

# Create virtual environment if it does not already exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies..."
pip install --quiet -r requirements.txt
pip install --quiet pytest-cov

Write-Host "Running tests..."
pytest tests/ -v --cov=xmlcompare --cov-report=term-missing

Write-Host "Build complete." -ForegroundColor Green
