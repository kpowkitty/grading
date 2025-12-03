from pathlib import Path
import os
import sys
import signal
from contextlib import contextmanager

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from grader.extract import prepare_submissions_folder, unzip_submission, flatten
from grader.compile import compile_cpp_files, link_executable, run_executable
from grader.design_check import (
    check_program_design,
    check_smart_pointers,
    check_friend_operator_overload,
    check_big3_implementation,
    check_linkedbag_operator_overload,
    check_test_case_files,
    print_source_files
)

# Configuration
ROOT_FOLDER = str(Path(__file__).resolve().parent.parent)
TEST_FILES_FOLDER = os.path.join(ROOT_FOLDER, "testing_files")
REQUIRED_PROGRAM_FILES = [
    "EventTicket340.cpp",
    "Organizer.cpp",
    "Event.cpp",
    "VirtualEvent.cpp",
    "VenueEvent.cpp"
]
LOG_FILE = "grading_output.txt"


@contextmanager
def timeout(seconds):
    """Context manager for timing out operations"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


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
                print(f"\n{'='*70}")
                print(f"Processing: {entry}")
                print(f"{'='*70}\n")

                try:
                    # Overall timeout for entire submission (5 minutes)
                    with timeout(300):
                        # 3. Unzip / flatten if needed
                        if os.path.isdir(entry):
                            fname = entry
                        else:
                            fname = unzip_submission(entry)

                        # Flatten but preserve LinkedBagDS directory
                        flatten(fname, exclude_dirs=['LinkedBagDS'])

                        # ============================================================
                        # ASSIGNMENT 3 GRADING CHECKS
                        # ============================================================
                        print("\n" + "="*60)
                        print("ASSIGNMENT 3 GRADING CHECKS")
                        print("="*60 + "\n")

                        # ------------------------------------------------------------
                        # Part 1: Smart Pointers (25 pts)
                        # ------------------------------------------------------------
                        print("--- Part 1: Smart Pointers (25 pts) ---")
                        print("LinkedBag of pointers: 10 pts")
                        print("Correct use of smart pointers: 15 pts")
                        print("  - Right type of smart pointers")
                        print("  - Pointers correctly created")
                        print("  - Pointers correctly used")
                        print("  - Correct use of polymorphism")
                        print()

                        try:
                            with timeout(30):
                                smart_ptr_results = check_smart_pointers(fname)
                        except TimeoutError:
                            print("✗ TIMEOUT: Smart pointer check took too long")
                            smart_ptr_results = {}

                        # ------------------------------------------------------------
                        # Part 2: Friend Functions (25 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 2: Friend Functions (25 pts) ---")

                        # EventTicket340 (operator<< only) - 3.5 pts
                        print("\nEventTicket340 (operator<< only) - 3.5 pts:")
                        try:
                            with timeout(10):
                                check_friend_operator_overload(fname, 'EventTicket340', ['<<'])
                        except TimeoutError:
                            print("✗ TIMEOUT: EventTicket340 operator check took too long")

                        # Organizer (<< and >>) - 3.5 + 3.5 pts
                        print("\nOrganizer (operator<< and operator>>) - 7 pts:")
                        try:
                            with timeout(10):
                                check_friend_operator_overload(fname, 'Organizer', ['<<', '>>'])
                        except TimeoutError:
                            print("✗ TIMEOUT: Organizer operator check took too long")

                        # VirtualEvent (<< and >>) - 3.75 + 3.5 pts
                        print("\nVirtualEvent (operator<< and operator>>) - 7.25 pts:")
                        try:
                            with timeout(10):
                                check_friend_operator_overload(fname, 'VirtualEvent', ['<<', '>>'])
                        except TimeoutError:
                            print("✗ TIMEOUT: VirtualEvent operator check took too long")

                        # VenueEvent (<< and >>) - 3.75 + 3.5 pts
                        print("\nVenueEvent (operator<< and operator>>) - 7.25 pts:")
                        try:
                            with timeout(10):
                                check_friend_operator_overload(fname, 'VenueEvent', ['<<', '>>'])
                        except TimeoutError:
                            print("✗ TIMEOUT: VenueEvent operator check took too long")

                        # ------------------------------------------------------------
                        # Part 3: BIG 3 - EventTicket340 (7 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 3: BIG 3 - EventTicket340 (7 pts) ---")
                        print("Destructor: 2 pts | Copy constructor: 2 pts | operator=: 3 pts")
                        try:
                            with timeout(10):
                                check_big3_implementation(fname, 'EventTicket340')
                        except TimeoutError:
                            print("✗ TIMEOUT: EventTicket340 Big 3 check took too long")

                        # ------------------------------------------------------------
                        # Part 3: BIG 3 - Organizer (15 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 3: BIG 3 - Organizer (15 pts) ---")
                        print("Destructor: 5 pts | Copy constructor: 5 pts | operator=: 5 pts")
                        try:
                            with timeout(10):
                                check_big3_implementation(fname, 'Organizer')
                        except TimeoutError:
                            print("✗ TIMEOUT: Organizer Big 3 check took too long")

                        # ------------------------------------------------------------
                        # Part 3: BIG 3 - VirtualEvent (8 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 3: BIG 3 - VirtualEvent (8 pts) ---")
                        print("Destructor: 2 pts | Copy constructor: 3 pts | operator=: 3 pts")
                        try:
                            with timeout(10):
                                check_big3_implementation(fname, 'VirtualEvent')
                        except TimeoutError:
                            print("✗ TIMEOUT: VirtualEvent Big 3 check took too long")

                        # ------------------------------------------------------------
                        # Part 3: BIG 3 - VenueEvent (8 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 3: BIG 3 - VenueEvent (8 pts) ---")
                        print("Destructor: 2 pts | Copy constructor: 3 pts | operator=: 3 pts")
                        try:
                            with timeout(10):
                                check_big3_implementation(fname, 'VenueEvent')
                        except TimeoutError:
                            print("✗ TIMEOUT: VenueEvent Big 3 check took too long")

                        # ------------------------------------------------------------
                        # Part 4: Design Decision (12 pts) - MANUALLY GRADED
                        # ------------------------------------------------------------
                        print("\n--- Part 4: Design Decision (12 pts) ---")
                        print("⚠ MANUALLY GRADE: Check if answer considers all 4 criteria")
                        print("  and explains clearly the reasons behind the choice of data structure.")

                        # ------------------------------------------------------------
                        # EC3: LinkedBag operator= overloading (10 pts)
                        # ------------------------------------------------------------
                        print("\n--- EC3: LinkedBag operator= overloading (10 pts) ---")
                        print("Prototype in .h file + implementation in .cpp file")
                        try:
                            with timeout(10):
                                check_linkedbag_operator_overload(fname)
                        except TimeoutError:
                            print("✗ TIMEOUT: LinkedBag operator= check took too long")

                        # ------------------------------------------------------------
                        # EC4: Non-trivial test case (5 pts)
                        # ------------------------------------------------------------
                        print("\n--- EC4: Non-trivial test case (5 pts) ---")
                        print("Menu options as input + expected behavior (2.5 pts each)")
                        try:
                            with timeout(5):
                                check_test_case_files(fname)
                        except TimeoutError:
                            print("✗ TIMEOUT: Test case file check took too long")

                        # ============================================================
                        # FILE STRUCTURE
                        # ============================================================
                        print("\n" + "-"*70)
                        print("FILE STRUCTURE")
                        print("-"*70)
                        try:
                            with timeout(10):
                                check_program_design(fname, REQUIRED_PROGRAM_FILES)
                        except TimeoutError:
                            print("✗ TIMEOUT: file structure check took too long")

                        # ============================================================
                        # SOURCE FILE CONTENTS
                        # ============================================================
                        print_source_files(fname)

                        # ============================================================
                        # COMPILATION AND EXECUTION
                        # ============================================================
                        print("\n" + "-"*70)
                        print("COMPILATION AND EXECUTION")
                        print("-"*70)
                        cwd = os.getcwd()
                        os.chdir(fname)
                        try:
                            with timeout(60):  # Compilation timeout
                                o_files = compile_cpp_files()
                                executable_name = f"{Path(fname).name}_output"
                                link_executable(o_files, executable_name)

                            # Try to run with very short timeout
                            print(f"\nAttempting to run {executable_name}...")
                            try:
                                with timeout(3):  # 3 second timeout
                                    run_executable(executable_name)
                            except TimeoutError:
                                print("✓ Executable started (timed out waiting for input - this is OK)")

                        except TimeoutError:
                            print("✗ TIMEOUT: Compilation took too long")
                        except Exception as compile_error:
                            print(f"✗ Compilation/Execution failed: {compile_error}")
                        finally:
                            os.chdir(cwd)

                        print(f"\n{'='*70}")
                        print(f"Completed: {entry}")
                        print(f"{'='*70}\n")

                except TimeoutError:
                    print(f"\n✗ OVERALL TIMEOUT: Processing {entry} exceeded 5 minutes")
                    print(f"Skipping to next submission...\n")
                except Exception as e:
                    print(f"Error processing {entry}: {e}\n")
                    import traceback
                    traceback.print_exc()

        finally:
            # Restore normal stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    print(f"Grading complete. Output written to {LOG_FILE}")
