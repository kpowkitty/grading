#!/bin/bash
# Compare two source files after stripping comments
# Usage: ./compare_two.sh file1.cpp file2.cpp

if [ $# -ne 2 ]; then
    echo "Usage: $0 <file1> <file2>"
    exit 1
fi

FILE1="$1"
FILE2="$2"

if [ ! -f "$FILE1" ]; then
    echo "Error: $FILE1 not found"
    exit 1
fi

if [ ! -f "$FILE2" ]; then
    echo "Error: $FILE2 not found"
    exit 1
fi

# Create temp files
TEMP1=$(mktemp)
TEMP2=$(mktemp)

# Strip comments from file 1
python3 -c "
import re
import sys

with open('$FILE1', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Remove single-line comments
content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
# Remove multi-line comments
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
# Remove empty lines
lines = [line.rstrip() for line in content.split('\n') if line.strip()]

with open('$TEMP1', 'w') as f:
    f.write('\n'.join(lines))
"

# Strip comments from file 2
python3 -c "
import re
import sys

with open('$FILE2', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Remove single-line comments
content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
# Remove multi-line comments
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
# Remove empty lines
lines = [line.rstrip() for line in content.split('\n') if line.strip()]

with open('$TEMP2', 'w') as f:
    f.write('\n'.join(lines))
"

echo "=== Comparing ==="
echo "File 1: $FILE1"
echo "File 2: $FILE2"
echo ""

# Count lines
LINES1=$(wc -l < "$TEMP1")
LINES2=$(wc -l < "$TEMP2")
echo "Lines (after stripping comments):"
echo "  File 1: $LINES1"
echo "  File 2: $LINES2"
echo ""

# Run diff
echo "=== Diff Output ==="
diff "$TEMP1" "$TEMP2"
DIFF_EXIT=$?

echo ""
echo "=== Summary ==="
if [ $DIFF_EXIT -eq 0 ]; then
    echo "Files are IDENTICAL (after stripping comments)"
else
    # Count identical lines
    IDENTICAL=$(comm -12 <(sort "$TEMP1") <(sort "$TEMP2") | wc -l)
    echo "Identical lines: $IDENTICAL"
fi

# Cleanup
rm "$TEMP1" "$TEMP2"
