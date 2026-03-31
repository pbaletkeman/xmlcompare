#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "=== xmlcompare Java build ==="
echo "--- Building with Gradle ---"
./gradlew clean build
echo "--- Building with Maven ---"
mvn clean package -q
echo "Build complete."
