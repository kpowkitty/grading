from grader.extract import prepare_submissions_folder, unzip_submission, flatten_inner_folder
from grader.compile import compile_cpp_files, link_executable, run_executable
from grader.design_check import move_test_files, check_program_design, print_library_files
from pathlib import Path
import os
import sys

# Configuration
ROOT_FOLDER = str(Path(__file__).resolve().parent.parent)
TEST_FILES_FOLDER = os.path.join(ROOT_FOLDER, "testing_files")
REQUIRED_PROGRAM_FILES = ["myLibrary.hpp", "myLibrary.cpp", "testing.cpp"]
LOG_FILE = "grading_output.txt"

if __name__ == "__main__":
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        # Redirect stdout/stderr to log file
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = f
        sys.stderr = f

        try:
            # 1. Prepare submissions folder
            submissions_path = prepare_submissions_folder(ROOT_FOLDER)
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
                    flatten_inner_folder(fname)

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

    print(f"Grading complete. Output written to {LOG_FILE}")
