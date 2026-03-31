@echo off
echo === xmlcompare Java build ===
cd /d "%~dp0"
echo --- Building with Gradle ---
gradlew.bat clean build
if errorlevel 1 exit /b 1
echo --- Building with Maven ---
mvn clean package -q
if errorlevel 1 exit /b 1
echo Build complete.
