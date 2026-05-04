from pathlib import Path
import os
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from grader.extract import unzip_submission, flatten
from grader.regrade import setup_regrade_args, prepare_submission_path
from grader.compile import compile_cpp_files, link_executable, run_executable
from grader.design_check import move_test_files, check_program_design, print_library_files

# Configuration
ROOT_FOLDER = str(Path(__file__).resolve().parent.parent)
ASSIGNMENT_MISC = "1_assignment_misc"
TESTING_FILES = "testing_files"
TEST_FILES_FOLDER = os.path.join(ROOT_FOLDER, ASSIGNMENT_MISC, TESTING_FILES)
REQUIRED_PROGRAM_FILES = ["myLibrary.hpp", "myLibrary.cpp", "testing.cpp"]

if __name__ == "__main__":
    args = setup_regrade_args()
    submissions_path, log_file = prepare_submission_path(args, ROOT_FOLDER)

    with open(log_file, "w", encoding="utf-8") as f:
        # Redirect stdout/stderr to log file
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = f
        sys.stderr = f

        try:
            # 1. Change to submissions folder
            os.chdir(submissions_path)

            # 2. Loop through each submission (zip or folder)
            entries = [e for e in os.listdir(".") if e.endswith(".zip") or os.path.isdir(e)]
            for entry in entries:
                print(f"\n---------------------------------- Processing: {entry} ---")
                try:
                    # 3. Unzip / flatten if needed
                    if os.path.isdir(entry):
                        fname = entry
                    else:
                        fname = unzip_submission(entry)
                    flatten(fname)

                    # 4. Check program design / print libraries / move test files
                    print_library_files(fname)
                    check_program_design(fname, REQUIRED_PROGRAM_FILES)
                    move_test_files(fname, TEST_FILES_FOLDER)

                    # 5. Compile, link, and run executable
                    cwd = os.getcwd()
                    os.chdir(fname)
                    try:
                        o_files = compile_cpp_files()
                        executable_name = f"{Path(fname).name}_output"
                        link_executable(o_files, executable_name)
                        run_executable(executable_name)
                    finally:
                        os.chdir(cwd)

                    print(f"Completed: {entry}\n")
                except Exception as e:
                    print(f"Error processing {entry}: {e}\n")

        finally:
            # Restore normal stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    print(f"Grading complete. Output written to {log_file}")
