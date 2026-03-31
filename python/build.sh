#!/usr/bin/env bash
# build.sh – Set up virtual environment, install dependencies, and run tests
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== xmlcompare Python build ==="

# Create virtual environment if it does not already exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate
source .venv/bin/activate

echo "Installing dependencies..."
pip install --quiet -r requirements.txt
pip install --quiet pytest-cov

echo "Running tests..."
pytest tests/ -v --cov=xmlcompare --cov-report=term-missing

echo "Build complete."
