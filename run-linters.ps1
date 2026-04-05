#!/usr/bin/env pwsh

<#
.SYNOPSIS
    PowerShell script to run all linters (ruff for Python, checkstyle for Java)

.DESCRIPTION
    Runs both Python ruff linter and Java checkstyle linter, providing a summary
    of results and returning appropriate exit code.

.EXAMPLE
    .\run-linters.ps1
#>

param(
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Continue"
$lintersFailed = $false

Write-Host ""
Write-Host "============================================================"
Write-Host "Running Linters"
Write-Host "============================================================"
Write-Host ""

# Python ruff linter
Write-Host "[1/2] Running Python linter (ruff)..." -ForegroundColor Cyan
Write-Host ""
Push-Location python
$pythonOutput = & python -m ruff check . --no-cache 2>&1
$pythonExitCode = $LASTEXITCODE

if ($pythonExitCode -ne 0) {
    Write-Host "ERROR: Python linter found issues" -ForegroundColor Red
    if ($Verbose) {
        Write-Host $pythonOutput
    }
    $lintersFailed = $true
} else {
    Write-Host "SUCCESS: Python linting passed" -ForegroundColor Green
}
Pop-Location
Write-Host ""

# Java checkstyle linter
Write-Host "[2/2] Running Java linter (checkstyle)..." -ForegroundColor Cyan
Write-Host ""
Push-Location java
$javaOutput = & mvn checkstyle:check -q 2>&1
$javaExitCode = $LASTEXITCODE

if ($javaExitCode -ne 0) {
    Write-Host "ERROR: Java linter found issues" -ForegroundColor Red
    if ($Verbose) {
        Write-Host $javaOutput
    }
    $lintersFailed = $true
} else {
    Write-Host "SUCCESS: Java linting passed" -ForegroundColor Green
}
Pop-Location
Write-Host ""

# Summary
Write-Host "============================================================"
if (-not $lintersFailed) {
    Write-Host "All linters passed!" -ForegroundColor Green
    Write-Host "============================================================"
    exit 0
} else {
    Write-Host "Some linters reported issues. See above for details." -ForegroundColor Red
    Write-Host "============================================================"
    exit 1
}
