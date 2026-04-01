#!/usr/bin/env bash
# fatjar.sh – Build the xmlcompare fat JAR (uber JAR with all dependencies)
# Usage: ./fatjar.sh [maven|gradle]  (defaults to maven)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BUILD_TOOL="${1:-maven}"

echo "=== xmlcompare fat JAR build ==="

case "$BUILD_TOOL" in
    maven|mvn)
        echo "Building fat JAR with Maven (maven-shade-plugin)..."
        mvn clean package -DskipTests -q
        echo ""
        echo "Fat JAR: target/xmlcompare-1.0.0.jar"
        ;;
    gradle)
        echo "Building fat JAR with Gradle..."
        ./gradlew clean jar
        echo ""
        echo "Fat JAR: build/libs/xmlcompare-1.0.0.jar"
        ;;
    *)
        echo "Unknown build tool: $BUILD_TOOL"
        echo "Usage: $0 [maven|gradle]"
        exit 1
        ;;
esac

echo "Build complete."
