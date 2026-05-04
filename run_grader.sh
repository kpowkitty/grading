#!/usr/bin/env bash

set -e

usage() {
    echo "Usage: $0 <class> <script_name> <output_file>"
    echo ""
    echo "Arguments:"
    echo "  class         Class subdir under classes/ (e.g., csc340, csc641)"
    echo "  script_name   Name of the Python script to run (without .py extension)"
    echo "  output_file   Name of the output file to remove (without .txt extension)"
    echo ""
    echo "Example:"
    echo "  $0 csc340 4_assignment_grader grading_output"
    echo "  $0 csc641 milestone2_grader grading_output"
    echo ""
    echo "This will:"
    echo "  1. Clean up classes/<class>/submissions_unzip/ (remove extracted folders)"
    echo "  2. Remove <output_file>.txt"
    echo "  3. Remove any .zip and .pdf files in submissions_unzip/"
    echo "  4. Run classes/<class>/scripts/<script_name>.py"
    exit 1
}

if [ $# -ne 3 ]; then
    echo "Error: Expected 3 arguments, got $#"
    echo ""
    usage
fi

CLASS="$1"
SCRIPT="$2"
OUTPUT="$3"

CLASS_DIR="classes/${CLASS}"
SUBMISSIONS="${CLASS_DIR}/submissions_unzip"
SCRIPTS="${CLASS_DIR}/scripts"

# Verify class dir exists
if [ ! -d "${CLASS_DIR}" ]; then
    echo "Error: Class directory '${CLASS_DIR}' not found"
    echo "Available classes:"
    ls classes/ 2>/dev/null || echo "  (none)"
    exit 1
fi

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
