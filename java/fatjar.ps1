# fatjar.ps1 – Build the xmlcompare fat JAR (uber JAR with all dependencies)
# Usage: .\fatjar.ps1 [-BuildTool maven|gradle]  (defaults to maven)
param(
    [ValidateSet("maven", "mvn", "gradle")]
    [string]$BuildTool = "maven"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=== xmlcompare fat JAR build ===" -ForegroundColor Cyan

if ($BuildTool -in @("maven", "mvn")) {
    Write-Host "Building fat JAR with Maven (maven-shade-plugin)..."
    & mvn clean package -DskipTests -q
    Write-Host ""
    Write-Host "Fat JAR: target/xmlcompare-1.0.0.jar" -ForegroundColor Yellow
} else {
    Write-Host "Building fat JAR with Gradle..."
    & ./gradlew clean jar
    Write-Host ""
    Write-Host "Fat JAR: build/libs/xmlcompare-1.0.0.jar" -ForegroundColor Yellow
}

Write-Host "Build complete." -ForegroundColor Green
