#!/usr/bin/env bash
# wheel.sh – Build the xmlcompare Python wheel
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== xmlcompare Python wheel build ==="

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing build tools..."
pip install --quiet --upgrade pip build wheel

echo "Cleaning previous dist..."
rm -rf dist/ xmlcompare.egg-info/

echo "Building wheel..."
python -m build --wheel

echo ""
echo "Wheel files:"
ls dist/*.whl

echo ""
echo "Done. Wheel is in the dist/ folder."
