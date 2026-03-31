$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
$JAR = "build/libs/xmlcompare-1.0.0.jar"
if (-not (Test-Path $JAR)) {
    Write-Error "JAR not found. Run ./build.ps1 first."
    exit 1
}
java -jar $JAR @args
