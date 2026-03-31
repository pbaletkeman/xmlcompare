@echo off
cd /d "%~dp0"
set JAR=build\libs\xmlcompare-1.0.0.jar
if not exist "%JAR%" (
    echo JAR not found. Run build.bat first. 1>&2
    exit /b 1
)
java -jar "%JAR%" %*
