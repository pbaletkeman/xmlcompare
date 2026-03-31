#!/usr/bin/env bash
# run.sh – Activate the virtual environment and run xmlcompare with any
#           arguments passed to this script.
#
# Usage:
#   ./run.sh --files samples/orders_expected.xml samples/orders_actual_diff.xml
#   ./run.sh --dirs samples/ samples/ --summary
#   ./run.sh --help
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run ./build.sh first." >&2
    exit 1
fi

source .venv/bin/activate
python xmlcompare.py "$@"
