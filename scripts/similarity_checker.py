#!/usr/bin/env python3
"""
Similarity checker for student submissions.
Compares source files across all submissions to detect potential plagiarism.
"""

import os
import re
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuration
ROOT_FOLDER = Path(__file__).resolve().parent.parent
SUBMISSIONS_FOLDER = ROOT_FOLDER / "submissions_unzip"
OUTPUT_FILE = ROOT_FOLDER / "similarity_report.txt"
SIMILARITY_THRESHOLD = 50  # Number of identical lines to flag

# Files/folders to skip
SKIP_DIRS = {'linkedbagds', '.git', '.vs', 'x64', 'debug', 'release', 'build',
             'cmake-build-debug', 'cmake-build-release', '__macosx'}
SKIP_PATTERNS = ['cmake', '.cmake', 'cmakelist']


def strip_comments(content: str) -> str:
    """Remove C/C++ comments from source code."""
    # Remove single-line comments
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    # Remove multi-line comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove empty lines and normalize whitespace
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    return '\n'.join(lines)


def should_skip_file(filename: str) -> bool:
    """Check if file should be skipped."""
    lower = filename.lower()
    # Skip dotfiles and Mac metadata
    if filename.startswith('.') or filename.startswith('._'):
        return True
    # Skip cmake files
    for pattern in SKIP_PATTERNS:
        if pattern in lower:
            return True
    return False


def should_skip_dir(dirname: str) -> bool:
    """Check if directory should be skipped."""
    return dirname.lower() in SKIP_DIRS


def get_source_files(submission_path: Path) -> dict:
    """
    Get all source files from a submission.
    Returns dict mapping filename -> full path
    """
    source_files = {}

    for root, dirs, files in os.walk(submission_path):
        # Filter out skipped directories
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]

        for f in files:
            if should_skip_file(f):
                continue
            if f.endswith('.cpp') or f.endswith('.h'):
                # Use just filename as key (not full path)
                source_files[f] = Path(root) / f

    return source_files


def count_identical_lines(content1: str, content2: str) -> int:
    """Count number of identical non-empty lines between two files."""
    lines1 = set(content1.split('\n'))
    lines2 = set(content2.split('\n'))
    # Remove empty lines from consideration
    lines1.discard('')
    lines2.discard('')
    return len(lines1.intersection(lines2))


def compare_files(file1: Path, file2: Path) -> tuple:
    """
    Compare two files after stripping comments.
    Returns (identical_lines, total_lines_file1, total_lines_file2)
    """
    try:
        with open(file1, 'r', encoding='utf-8', errors='ignore') as f:
            content1 = strip_comments(f.read())
        with open(file2, 'r', encoding='utf-8', errors='ignore') as f:
            content2 = strip_comments(f.read())

        identical = count_identical_lines(content1, content2)
        total1 = len([l for l in content1.split('\n') if l])
        total2 = len([l for l in content2.split('\n') if l])

        return identical, total1, total2
    except Exception as e:
        print(f"Error comparing files: {e}")
        return 0, 0, 0


def main():
    print(f"Similarity Checker")
    print(f"==================")
    print(f"Submissions folder: {SUBMISSIONS_FOLDER}")
    print(f"Threshold: {SIMILARITY_THRESHOLD} identical lines")
    print()

    if not SUBMISSIONS_FOLDER.exists():
        print(f"Error: Submissions folder not found: {SUBMISSIONS_FOLDER}")
        return

    # Get all submission folders
    submissions = [d for d in SUBMISSIONS_FOLDER.iterdir()
                   if d.is_dir() and not d.name.startswith('.')]
    submissions.sort()

    print(f"Found {len(submissions)} submissions")
    print()

    # Collect all source files from each submission
    submission_files = {}
    for sub in submissions:
        submission_files[sub.name] = get_source_files(sub)

    # Track similarities
    similarities = []

    # Compare each submission against all others
    for i, sub1_name in enumerate(submission_files.keys()):
        sub1_files = submission_files[sub1_name]

        for sub2_name in list(submission_files.keys())[i+1:]:
            sub2_files = submission_files[sub2_name]

            # Compare files with matching names
            common_files = set(sub1_files.keys()) & set(sub2_files.keys())

            for filename in common_files:
                file1 = sub1_files[filename]
                file2 = sub2_files[filename]

                identical, total1, total2 = compare_files(file1, file2)

                if identical >= SIMILARITY_THRESHOLD:
                    similarity = {
                        'student1': sub1_name,
                        'student2': sub2_name,
                        'file': filename,
                        'identical_lines': identical,
                        'total_lines_1': total1,
                        'total_lines_2': total2,
                        'file1_path': str(file1),
                        'file2_path': str(file2)
                    }
                    similarities.append(similarity)

                    # Print to console
                    print(f"SIMILARITY FOUND:")
                    print(f"  Students: {sub1_name} <-> {sub2_name}")
                    print(f"  File: {filename}")
                    print(f"  Identical lines: {identical}")
                    print(f"  File 1: {file1} ({total1} lines)")
                    print(f"  File 2: {file2} ({total2} lines)")
                    print()

    # Write report to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Similarity Report\n")
        f.write(f"=================\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Submissions folder: {SUBMISSIONS_FOLDER}\n")
        f.write(f"Threshold: {SIMILARITY_THRESHOLD} identical lines\n")
        f.write(f"Total submissions: {len(submissions)}\n")
        f.write(f"\n")

        if similarities:
            f.write(f"SIMILARITIES FOUND: {len(similarities)}\n")
            f.write(f"{'='*60}\n\n")

            # Group by student pairs
            pair_similarities = defaultdict(list)
            for sim in similarities:
                pair = (sim['student1'], sim['student2'])
                pair_similarities[pair].append(sim)

            for pair, sims in pair_similarities.items():
                f.write(f"Students: {pair[0]} <-> {pair[1]}\n")
                f.write(f"-" * 50 + "\n")
                for sim in sims:
                    f.write(f"  File: {sim['file']}\n")
                    f.write(f"    Identical lines: {sim['identical_lines']}\n")
                    f.write(f"    Path 1: {sim['file1_path']} ({sim['total_lines_1']} lines)\n")
                    f.write(f"    Path 2: {sim['file2_path']} ({sim['total_lines_2']} lines)\n")
                f.write(f"\n")
        else:
            f.write("No similarities found above threshold.\n")

    # Summary
    print(f"{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total submissions checked: {len(submissions)}")
    print(f"Total similarities found: {len(similarities)}")

    if similarities:
        # Get unique student pairs
        pairs = set((s['student1'], s['student2']) for s in similarities)
        print(f"Student pairs with similarities: {len(pairs)}")
        print()
        print("Pairs:")
        for pair in sorted(pairs):
            pair_sims = [s for s in similarities
                        if s['student1'] == pair[0] and s['student2'] == pair[1]]
            print(f"  {pair[0]} <-> {pair[1]}: {len(pair_sims)} file(s)")

    print()
    print(f"Full report written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
