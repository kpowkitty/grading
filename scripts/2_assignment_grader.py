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
    move_test_files,
    check_program_design,
    check_class_files_exist,
    find_inheritance,
    check_function_exists_in_file,
    check_function_usage,
    count_pattern_in_files,
    check_keyword_in_files,
    check_files_exist,
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

# ADD TIMEOUT CONTEXT MANAGER HERE
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
                    # ADD OVERALL TIMEOUT FOR ENTIRE SUBMISSION (5 minutes)
                    with timeout(300):
                        # 3. Unzip / flatten if needed
                        if os.path.isdir(entry):
                            fname = entry
                        else:
                            fname = unzip_submission(entry)
                        
                        # Flatten but preserve LinkedBagDS directory
                        flatten(fname, exclude_dirs=['LinkedBagDS'])
                        
                        # 4. Assignment 2 Specific Checks
                        print("\n" + "="*60)
                        print("ASSIGNMENT 2 GRADING CHECKS")
                        print("="*60 + "\n")
                        
                        # Part 3: LinkedBag function "reverseAppendK" (10 pts)
                        print("--- Part 3: LinkedBag function 'reverseAppendK' (10 pts) ---")
                        print("Implementation: 6 pts | Use in program: 4 pts")
                        try:
                            with timeout(10):
                                reverseAppendK_impl = check_function_exists_in_file(
                                    fname,
                                    'linkedbag',
                                    ['reverseAppendK']
                                )
                        except TimeoutError:
                            print("✗ TIMEOUT: reverseAppendK check took too long")
                            reverseAppendK_impl = {}
                        
                        print("\nChecking reverseAppendK usage in program:")
                        try:
                            with timeout(10):
                                reverseAppendK_usage = check_function_usage(fname, ['reverseAppendK'])
                        except TimeoutError:
                            print("✗ TIMEOUT: reverseAppendK usage check took too long")
                            reverseAppendK_usage = {}
                        
                        # Part 3: LinkedBag function "findKthItem" (10 pts)
                        print("\n--- Part 3: LinkedBag function 'findKthItem' (10 pts) ---")
                        print("Implementation: 6 pts | Use in program: 4 pts")
                        try:
                            with timeout(10):
                                findKthItem_impl = check_function_exists_in_file(
                                    fname,
                                    'linkedbag',
                                    ['findKthItem']
                                )
                        except TimeoutError:
                            print("✗ TIMEOUT: findKthItem check took too long")
                            findKthItem_impl = {}
                        
                        print("\nChecking findKthItem usage in program:")
                        try:
                            with timeout(10):
                                findKthItem_usage = check_function_usage(fname, ['findKthItem'])
                        except TimeoutError:
                            print("✗ TIMEOUT: findKthItem usage check took too long")
                            findKthItem_usage = {}
                        
                        # Part 1: UML Class Diagram (25 pts) - MANUALLY GRADED
                        print("\n--- Part 1: UML Class Diagram (25 pts) ---")
                        print("⚠ MANUALLY GRADE PDF: 5 pts per class (fields, functions, links)")
                        print("Classes: EventTicket340, Organizer, Event, VirtualEvent, VenueEvent")
                        
                        # Part 2: Programming Style (3 pts) - MANUALLY GRADED
                        print("\n--- Part 2: Programming Style (3 pts) ---")
                        print("⚠ MANUALLY GRADE: Meaningful variables, indentation, consistency, documentation")
                        
                        # Part 2: Program Design - Classes in separate files (5 pts - 1 pt each)
                        print("\n--- Part 2: Program Design -- Classes in separate .cpp and .h files (5 pts) ---")
                        print("1 pt for each class")
                        required_classes = [
                            "EventTicket340",
                            "Organizer", 
                            "Event",
                            "VirtualEvent",
                            "VenueEvent"
                        ]
                        try:
                            with timeout(30):  # This one might take longer
                                class_results = check_class_files_exist(fname, required_classes)
                        except TimeoutError:
                            print("✗ TIMEOUT: check_class_files_exist took too long")
                            class_results = {}
                        
                        # Part 2: Program Design - Inheritance (4 pts)
                        print("\n--- Part 2: Program Design -- At least one instance of inheritance (4 pts) ---")
                        try:
                            with timeout(20):
                                inheritance = find_inheritance(fname)
                                if inheritance:
                                    print(f"✓ Inheritance requirement met ({len(inheritance)} instance(s) found)")
                                else:
                                    print("✗ No inheritance found")
                        except TimeoutError:
                            print("✗ TIMEOUT: find_inheritance took too long")
                            inheritance = []
                        
                        # Part 2: Program Design - Single list (4 pts)
                        print("\n--- Part 2: Program Design -- Single list for all products (4 pts) ---")
                        try:
                            with timeout(10):
                                linkedbag_count = count_pattern_in_files(
                                    fname, 
                                    'organizer',
                                    r'LinkedBag\s*<[^>]+>\s+\w+\s*;'
                                )
                                if linkedbag_count == 1:
                                    print("✓ Single list design: Found exactly 1 LinkedBag declaration")
                                elif linkedbag_count > 1:
                                    print(f"✗ Multiple lists found: {linkedbag_count} LinkedBag declarations")
                                else:
                                    print("✗ No LinkedBag declarations found in Organizer")
                        except TimeoutError:
                            print("✗ TIMEOUT: count_pattern_in_files took too long")
                            linkedbag_count = 0
                        
                        # Part 2: Program Correctness - Main runs on terminal (2 pts)
                        print("\n--- Part 2: Program Correctness -- Main runs on terminal (2 pts) ---")
                        print("⚠ CHECK COMPILATION OUTPUT BELOW")
                        
                        # Part 2: Program Correctness - Menu implementation (32 pts)
                        print("\n--- Part 2: Program Correctness -- displayUserMenu and 9 menu options (32 pts) ---")
                        print("displayOrganizerMenu: 3 pts | create/edit event: 4 pts each | other options: 3 pts each")
                        
                        try:
                            with timeout(10):
                                menu_check = check_keyword_in_files(
                                    fname,
                                    'main',
                                    [
                                        'displayorganizermenu', 
                                        'display_organizer_menu'
                                    ]
                                )
                                if menu_check.get('displayorganizermenu') or menu_check.get('display_organizer_menu'):
                                    print("✓ displayOrganizerMenu (3 pts)")
                                else:
                                    print("✗ displayOrganizerMenu not found (0 pts)")
                        except TimeoutError:
                            print("✗ TIMEOUT: menu check took too long")
                            menu_check = {}
                        
                        print("\nMenu options:")
                        menu_keywords = {
                            'create.*organizer': 'Create organizer (3 pts)',
                            'display.*information': 'Display information (3 pts)',
                            'modify.*password': 'Modify password (3 pts)',
                            'create.*event': 'Create event (4 pts)',
                            'display.*all.*event': 'Display all events (3 pts)',
                            'display.*kth.*event': 'Display kth event (3 pts)',
                            'modify.*event': 'Modify event (4 pts)',
                            'sell.*ticket': 'Sell ticket (3 pts)',
                            'delete.*event': 'Delete event (3 pts)'
                        }
                        
                        try:
                            with timeout(15):
                                menu_results = check_keyword_in_files(fname, 'main', list(menu_keywords.keys()))
                                for pattern, description in menu_keywords.items():
                                    if menu_results.get(pattern):
                                        print(f"✓ {description}")
                                    else:
                                        print(f"✗ {description}")
                        except TimeoutError:
                            print("✗ TIMEOUT: menu options check took too long")
                        
                        # Part 4: OOP principle 1 (7.5 pts) - MANUALLY GRADED
                        print("\n--- Part 4: OOP principle 1 (7.5 pts) ---")
                        print("⚠ MANUALLY GRADE PDF")
                        
                        # Part 4: OOP principle 2 (7.5 pts) - MANUALLY GRADED
                        print("\n--- Part 4: OOP principle 2 (7.5 pts) ---")
                        print("⚠ MANUALLY GRADE PDF")
                        
                        # Extra Credit (5 pts)
                        print("\n--- Extra Credit - Sample Input/Output (5 pts) ---")
                        try:
                            with timeout(5):
                                extra_credit = check_files_exist(fname, ['input01.txt', 'output01.txt'])
                                if extra_credit.get('input01.txt') and extra_credit.get('output01.txt'):
                                    print("✓ Both extra credit files found (5 pts)")
                                elif extra_credit.get('input01.txt') or extra_credit.get('output01.txt'):
                                    print("⚠ Only one extra credit file found")
                                else:
                                    print("✗ Extra credit files not found (0 pts)")
                        except TimeoutError:
                            print("✗ TIMEOUT: extra credit check took too long")

                        # 5. File structure checks
                        print("\n" + "-"*70)
                        print("FILE STRUCTURE")
                        print("-"*70)
                        try:
                            with timeout(10):
                                check_program_design(fname, REQUIRED_PROGRAM_FILES)
                        except TimeoutError:
                            print("✗ TIMEOUT: file structure check took too long")
                        
                        # Print all source files
                        print_source_files(fname)
                        
                        # 6. Compile, link, and run executable
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
