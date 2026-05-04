#!/usr/bin/env bash

set -e

SUBMISSIONS="submissions_unzip"
SCRIPTS="scripts"

usage() {
    echo "Usage: $0 <script_name> <output_file>"
    echo ""
    echo "Arguments:"
    echo "  script_name   Name of the Python script to run (without .py extension)"
    echo "  output_file   Name of the output file to remove (without .txt extension)"
    echo ""
    echo "Example:"
    echo "  $0 4_assignment_grader grading_output"
    echo ""
    echo "This will:"
    echo "  1. Clean up ${SUBMISSIONS}/ (remove extracted folders)"
    echo "  2. Remove <output_file>.txt"
    echo "  3. Remove any .zip and .pdf files in ${SUBMISSIONS}/"
    echo "  4. Run ${SCRIPTS}/<script_name>.py"
    exit 1
}

if [ $# -ne 2 ]; then
    echo "Error: Expected 2 arguments, got $#"
    echo ""
    usage
fi

SCRIPT="$1"
OUTPUT="$2"

# Verify script exists
if [ ! -f "${SCRIPTS}/${SCRIPT}.py" ]; then
    echo "Error: Script '${SCRIPTS}/${SCRIPT}.py' not found"
    exit 1
fi

echo "=== Cleaning up ==="

# Remove everything in submissions folder
if [ -d "${SUBMISSIONS}" ]; then
    rm -rv "${SUBMISSIONS}"/* 2>/dev/null || true
else
    echo "Warning: ${SUBMISSIONS}/ directory not found"
fi

# Remove output file
if [ -f "${OUTPUT}.txt" ]; then
    rm -v "${OUTPUT}.txt"
else
    echo "Note: ${OUTPUT}.txt does not exist, skipping"
fi

echo ""
echo "=== Running grader ==="
python "${SCRIPTS}/${SCRIPT}.py"

echo ""
echo "=== Cleaning up extracted files ==="
# Remove zip and pdf files after grading
if [ -d "${SUBMISSIONS}" ]; then
    rm -fv "${SUBMISSIONS}"/*.zip "${SUBMISSIONS}"/*.pdf 2>/dev/null || true
fi

echo ""
echo "=== Done ==="
