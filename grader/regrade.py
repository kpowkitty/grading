"""
Individual regrade handler module.

Usage in grader scripts:
    from grader.regrade import setup_regrade_args, prepare_submission_path

    if __name__ == "__main__":
        args = setup_regrade_args()
        submissions_path = prepare_submission_path(args, ROOT_FOLDER)
        # ... rest of grading logic
"""

import argparse
import os
import re
import zipfile
from datetime import datetime
from pathlib import Path

from grader.extract import prepare_submissions_folder


def setup_regrade_args():
    """
    Set up argument parser for individual regrades.

    Returns:
        argparse.Namespace with:
            - zip_file: str or None (the zip filename)
            - student_name: str or None (the student's name for folder)
    """
    parser = argparse.ArgumentParser(
        description='Grade assignments. Run without arguments for batch grading, '
                    'or provide zip file and student name for individual regrade.'
    )
    parser.add_argument(
        'zip_file',
        nargs='?',
        default=None,
        help='The zip file name (from ~/Downloads) for individual regrade'
    )
    parser.add_argument(
        'student_name',
        nargs='?',
        default=None,
        help='The student name (used for the output folder)'
    )

    args = parser.parse_args()

    # Validate: either both or neither
    if (args.zip_file is None) != (args.student_name is None):
        parser.error('Must provide both zip_file and student_name, or neither')

    return args


def extract_assignment_number(zip_filename: str) -> int:
    """
    Extract the assignment number from a zip filename.
    Handles single and multi-digit numbers (1, 2, ..., 10, 11, etc.)

    Args:
        zip_filename: The name of the zip file

    Returns:
        The assignment number as an integer

    Raises:
        ValueError: If no number found in filename
    """
    # \d+ matches one or more digits, so handles 1, 10, 100, etc.
    numbers = re.findall(r'\d+', zip_filename)

    if not numbers:
        raise ValueError(f"Could not extract assignment number from '{zip_filename}'")

    # Return the first number found
    return int(numbers[0])


def prepare_individual_submission(zip_file: str, student_name: str, root_folder: str) -> tuple:
    """
    Prepare an individual submission for regrading.

    Unzips the file from ~/Downloads into:
        individual_submissions/X_assignment/student_name_YYYY-MM-DD_HH-MM-SS/

    Args:
        zip_file: The zip filename (just the name, not full path)
        student_name: The student's name for the folder
        root_folder: The root folder of the grading project

    Returns:
        Tuple of (assignment_dir, log_file_path)
    """
    # Source path in Downloads
    downloads_path = Path.home() / "Downloads" / zip_file

    if not downloads_path.exists():
        raise FileNotFoundError(f"Zip file not found: {downloads_path}")

    # Extract assignment number
    assignment_num = extract_assignment_number(zip_file)

    # Build directory paths
    individual_submissions_dir = os.path.join(root_folder, "individual_submissions")
    assignment_dir = os.path.join(individual_submissions_dir, f"{assignment_num}_assignment")

    # Create student directory with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    student_dir_name = f"{student_name}_{timestamp}"
    student_dir = os.path.join(assignment_dir, student_dir_name)

    # Create directory hierarchy (each level)
    if not os.path.exists(individual_submissions_dir):
        os.makedirs(individual_submissions_dir)
        print(f"Created directory: {individual_submissions_dir}")

    if not os.path.exists(assignment_dir):
        os.makedirs(assignment_dir)
        print(f"Created directory: {assignment_dir}")

    os.makedirs(student_dir)
    print(f"Created directory: {student_dir}")

    # Extract zip to student directory
    print(f"Extracting {zip_file} to {student_dir}...")
    with zipfile.ZipFile(downloads_path, 'r') as zip_ref:
        zip_ref.extractall(student_dir)
    print("Extraction complete.")

    # Log file goes in the student directory
    log_file_path = os.path.join(student_dir, "grading_output.txt")

    return assignment_dir, log_file_path


def prepare_submission_path(args, root_folder: str) -> tuple:
    """
    Prepare the submission path based on arguments.

    If args has zip_file and student_name, prepares individual submission.
    Otherwise, calls the standard prepare_submissions_folder.

    Args:
        args: Parsed arguments from setup_regrade_args()
        root_folder: The root folder of the grading project

    Returns:
        Tuple of (submissions_path, log_file_path)
    """
    if args.zip_file is not None:
        # Individual regrade mode
        return prepare_individual_submission(args.zip_file, args.student_name, root_folder)
    else:
        # Batch mode - use standard function
        return prepare_submissions_folder(root_folder), "grading_output.txt"
