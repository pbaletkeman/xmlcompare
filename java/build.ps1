$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
Write-Host "=== xmlcompare Java build ==="
Write-Host "--- Building with Gradle ---"
& ./gradlew clean build
if ($LASTEXITCODE -ne 0) { exit 1 }
Write-Host "--- Building with Maven ---"
& mvn clean package -q
if ($LASTEXITCODE -ne 0) { exit 1 }
Write-Host "Build complete."
