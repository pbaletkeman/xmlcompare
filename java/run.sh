#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
JAR="build/libs/xmlcompare-1.0.0.jar"
if [ ! -f "$JAR" ]; then
    echo "JAR not found. Run ./build.sh first." >&2
    exit 1
fi
java -jar "$JAR" "$@"
