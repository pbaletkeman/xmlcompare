# run.ps1 – Activate the virtual environment and run xmlcompare with any
#            arguments passed to this script.
#
# Usage:
#   .\run.ps1 --files samples\orders_expected.xml samples\orders_actual_diff.xml
#   .\run.ps1 --dirs samples\ samples\ --summary
#   .\run.ps1 --help
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if (-not (Test-Path ".venv")) {
    Write-Error "Virtual environment not found. Run .\build.ps1 first."
    exit 1
}

& ".\.venv\Scripts\Activate.ps1"
python xmlcompare.py @Arguments
exit $LASTEXITCODE
