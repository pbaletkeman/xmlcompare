# wheel.ps1 – Build the xmlcompare Python wheel
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=== xmlcompare Python wheel build ===" -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"

Write-Host "Installing build tools..."
pip install --quiet --upgrade pip build wheel

Write-Host "Cleaning previous dist..."
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "xmlcompare.egg-info") { Remove-Item -Recurse -Force "xmlcompare.egg-info" }

Write-Host "Building wheel..."
python -m build --wheel

Write-Host ""
Write-Host "Wheel files:" -ForegroundColor Yellow
Get-ChildItem dist\*.whl | ForEach-Object { Write-Host "  $($_.Name)" }

Write-Host ""
Write-Host "Done. Wheel is in the dist/ folder." -ForegroundColor Green
