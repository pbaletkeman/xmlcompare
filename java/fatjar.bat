@echo off
REM fatjar.bat – Build the xmlcompare fat JAR (uber JAR with all dependencies)
REM Usage: fatjar.bat [maven|gradle]  (defaults to maven)
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo === xmlcompare fat JAR build ===

set BUILD_TOOL=%1
if "%BUILD_TOOL%"=="" set BUILD_TOOL=maven

if /i "%BUILD_TOOL%"=="maven" goto maven
if /i "%BUILD_TOOL%"=="mvn"   goto maven
if /i "%BUILD_TOOL%"=="gradle" goto gradle

echo Unknown build tool: %BUILD_TOOL%
echo Usage: fatjar.bat [maven^|gradle]
exit /b 1

:maven
echo Building fat JAR with Maven (maven-shade-plugin)...
call mvn clean package -DskipTests -q
if errorlevel 1 (
    echo Maven build failed.
    exit /b 1
)
echo.
echo Fat JAR: target\xmlcompare-1.0.0.jar
goto done

:gradle
echo Building fat JAR with Gradle...
call gradlew.bat clean jar
if errorlevel 1 (
    echo Gradle build failed.
    exit /b 1
)
echo.
echo Fat JAR: build\libs\xmlcompare-1.0.0.jar

:done
echo Build complete.
