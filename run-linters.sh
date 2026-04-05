#!/bin/bash

#
# Bash script to run all linters
# Runs ruff for Python and checkstyle for Java
#

set -e

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

LINTER_FAILED=0

echo ""
echo "============================================================"
echo "Running Linters"
echo "============================================================"
echo ""

# Python ruff linter
echo "[1/2] Running Python linter (ruff)..."
echo ""
cd python
if python -m ruff check . --no-cache; then
    echo "SUCCESS: Python linting passed"
else
    echo "ERROR: Python linter found issues"
    LINTER_FAILED=1
fi
cd ..
echo ""

# Java checkstyle linter
echo "[2/2] Running Java linter (checkstyle)..."
echo ""
cd java
if mvn checkstyle:check -q; then
    echo "SUCCESS: Java linting passed"
else
    echo "ERROR: Java linter found issues"
    LINTER_FAILED=1
fi
cd ..
echo ""

# Summary
echo "============================================================"
if [ $LINTER_FAILED -eq 0 ]; then
    echo "All linters passed!"
    echo "============================================================"
    exit 0
else
    echo "Some linters reported issues. See above for details."
    echo "============================================================"
    exit 1
fi
