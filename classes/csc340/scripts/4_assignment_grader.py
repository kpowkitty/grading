from pathlib import Path
import os
import sys
import signal
import re
import subprocess
from contextlib import contextmanager

project_root = next(p for p in Path(__file__).resolve().parents if (p / ".git").exists())
sys.path.insert(0, str(project_root))

from grader.extract import unzip_submission, flatten
from grader.regrade import setup_regrade_args, prepare_submission_path
from grader.compile import compile_cpp_files, link_executable, run_executable
import shutil
from grader.design_check import (
    check_program_design,
    check_files_exist,
    print_source_files,
    check_style_and_documentation,
    check_recursive_function,
    check_mergesort_genai,
    check_mergesort_linkedbag,
    check_quicksort_ec
)
from grader.utils import organize_flat_submission

# Configuration
ROOT_FOLDER = str(Path(__file__).resolve().parent.parent)
TEST_MAIN_PART1 = str(Path(__file__).resolve().parent.parent / "4_assignment_misc" / "testMain_Part1.cpp")
TEST_MAIN_GENAI = str(Path(__file__).resolve().parent.parent / "4_assignment_misc" / "testMain_GenAI.cpp")
TEST_MAIN_LINKEDBAG = str(Path(__file__).resolve().parent.parent / "4_assignment_misc" / "4_code" / "assignment4_code" / "Part3" / "linkedBagSortingMain.cpp")


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

                        # Flatten but preserve Part1, Part2, Part3, and LinkedBagDS directories
                        flatten(fname, exclude_dirs=['Part1', 'Part2', 'Part3', 'LinkedBagDS'])

                        # If Part1/Part3 don't exist, organize flat submission
                        organize_flat_submission(
                            fname,
                            ['Part1', 'Part3'],
                            [['seriesRecursive.cpp'], ['*']],
                            [[], ['LinkedBagDS']]  # Move LinkedBagDS into Part3
                        )

                        # ============================================================
                        # ASSIGNMENT 4 GRADING CHECKS
                        # ============================================================
                        print("\n" + "="*60)
                        print("ASSIGNMENT 4 GRADING CHECKS")
                        print("="*60 + "\n")

                        # Check Part1 folder exists
                        part1_path = os.path.join(fname, 'Part1')
                        if os.path.exists(part1_path) and os.path.isdir(part1_path):
                            print(f"✓ Part1 folder found")
                            try:
                                with timeout(10):
                                    check_style_and_documentation(part1_path, "Part1")
                            except TimeoutError:
                                print("✗ TIMEOUT: Style check took too long")
                        else:
                            print("✗ Part1 folder not found")

                        # ------------------------------------------------------------
                        # Part 1-1: Program Correctness - Main runs (2 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 1-1: Program Correctness - Main runs on terminal (2 pts) ---")

                        part1_compiles = False
                        if os.path.exists(part1_path) and os.path.isdir(part1_path):
                            cwd = os.getcwd()
                            os.chdir(part1_path)
                            try:
                                series_file = "seriesRecursive.cpp"
                                backup_file = "seriesRecursive_backup.bak"  # .bak so it won't be compiled
                                test_main_file = "testMain_Part1.cpp"

                                # Print seriesRecursive.cpp contents before testing
                                if os.path.exists(series_file):
                                    print(f"\n{'='*60}")
                                    print(f"FILE: {series_file}")
                                    print('='*60)
                                    try:
                                        with open(series_file, 'r', encoding='utf-8', errors='ignore') as f:
                                            print(f.read())
                                    except Exception as e:
                                        print(f"Error reading file: {e}")
                                    print('='*60 + "\n")

                                if os.path.exists(series_file):
                                    # Backup original file
                                    shutil.copy2(series_file, backup_file)

                                    # Read file and remove main function (from "int main" to EOF)
                                    with open(series_file, 'r', encoding='utf-8', errors='ignore') as f:
                                        lines = f.readlines()

                                    # Find line where main starts
                                    main_line = None
                                    for i, line in enumerate(lines):
                                        if 'int main' in line:
                                            main_line = i
                                            break

                                    if main_line is not None:
                                        # Keep only lines before main
                                        lines = lines[:main_line]
                                        print(f"✓ Removed main() from line {main_line + 1} to EOF")

                                    # Ensure function is named seriesRecursive
                                    content = ''.join(lines)
                                    # Replace common alternative names
                                    content = content.replace('series_recursive', 'seriesRecursive')
                                    content = content.replace('Series_Recursive', 'seriesRecursive')
                                    content = content.replace('SeriesRecursive', 'seriesRecursive')

                                    with open(series_file, 'w', encoding='utf-8') as f:
                                        f.write(content)

                                    # Copy test main
                                    if os.path.exists(TEST_MAIN_PART1):
                                        shutil.copy2(TEST_MAIN_PART1, test_main_file)
                                        print(f"✓ Copied test main")
                                    else:
                                        print(f"✗ Test main not found at {TEST_MAIN_PART1}")

                                print("\n--- PART 1 COMPILATION (with test main) ---")
                                with timeout(60):
                                    o_files = compile_cpp_files()
                                    executable_name = "Part1_output"
                                    link_executable(o_files, executable_name)
                                    part1_compiles = True

                                print(f"\n--- PART 1 EXECUTION (10 test cases) ---")
                                try:
                                    with timeout(30):
                                        run_executable(executable_name)
                                except TimeoutError:
                                    print("✗ TIMEOUT: Execution took too long (possible infinite recursion)")

                            except TimeoutError:
                                print("✗ TIMEOUT: Compilation took too long")
                            except Exception as compile_error:
                                print(f"✗ Compilation/Execution failed: {compile_error}")
                            finally:
                                # Restore original file
                                if os.path.exists(backup_file):
                                    shutil.move(backup_file, series_file)
                                # Clean up test main copy
                                if os.path.exists(test_main_file):
                                    os.remove(test_main_file)
                                os.chdir(cwd)
                        else:
                            print("✗ Part1 folder not found - cannot compile")

                        if part1_compiles:
                            print("\n✓ Part 1 compiles and runs (2 pts)")
                        else:
                            print("\n✗ Part 1 does NOT compile/run (0 pts)")
                        print()

                        # ------------------------------------------------------------
                        # Part 1-1: Program Correctness - Test cases (15 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 1-1: Program Correctness - All test cases correct (15 pts) ---")
                        print("No hard-coding allowed")

                        if os.path.exists(part1_path) and os.path.isdir(part1_path):
                            try:
                                with timeout(30):
                                    check_recursive_function(part1_path)
                            except TimeoutError:
                                print("✗ TIMEOUT: Recursive function check took too long")
                        print()

                        # ------------------------------------------------------------
                        # Part 3-1: mergeSortGenAI.cpp (10 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 3-1: mergeSortGenAI.cpp (10 pts) ---")
                        print("GenAI implementation for linked list (NOT LinkedBag)")

                        part3_path = os.path.join(fname, 'Part3')
                        if os.path.exists(part3_path) and os.path.isdir(part3_path):
                            print(f"✓ Part3 folder found")
                            try:
                                with timeout(10):
                                    check_mergesort_genai(part3_path)
                            except TimeoutError:
                                print("✗ TIMEOUT: mergeSortGenAI check took too long")

                            # Print mergeSortGenAI.cpp contents
                            genai_file = os.path.join(part3_path, 'mergeSortGenAI.cpp')
                            if os.path.exists(genai_file):
                                print("\n--- mergeSortGenAI.cpp contents ---")
                                try:
                                    with open(genai_file, 'r', encoding='utf-8', errors='ignore') as f:
                                        print(f.read())
                                except Exception as e:
                                    print(f"Error reading file: {e}")
                                print("--- end mergeSortGenAI.cpp ---")

                            # ------------------------------------------------------------
                            # Test GenAI merge sort with our test main
                            # ------------------------------------------------------------
                            if not os.path.exists(genai_file):
                                print("\n--- Testing GenAI Merge Sort ---")
                                print("✗ mergeSortGenAI.cpp not found - skipping GenAI test")
                            else:
                                print("\n--- Testing GenAI Merge Sort ---")

                                # Always copy our test main to their directory
                                test_main_genai_dest = os.path.join(part3_path, 'testMain_GenAI.cpp')
                                shutil.copy2(TEST_MAIN_GENAI, test_main_genai_dest)
                                print(f"✓ Copied testMain_GenAI.cpp to Part3")

                                # Read the GenAI file to find function signature
                                with open(genai_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    genai_content = f.read()

                                # Detect mergesort function pattern: Node* functionName(Node* ...)
                                # Look for functions that return a pointer and contain "mergesort" variations
                                # Must have both "merge" and "sort" to avoid helpers like "sortedMerge" or just "merge"
                                # Also handle static functions: static Node* mergeSort(...)
                                merge_func_match = re.search(
                                    r'(?:static\s+)?(?:struct\s+)?(\w+)\*\s+(\w*[Mm]erge[Ss]ort\w*|\w*[Ss]ort[Mm]erge\w*|sortList|sortLinkedList)\s*\(\s*(?:struct\s+)?(\w+)\*',
                                    genai_content
                                )

                                # Check for class - need this to know if function is a method
                                class_match = re.search(r'class\s+(\w+)', genai_content)

                                # Check for Node struct data member name and access pattern
                                # Detect if using getters (getData()) or direct access (->data)
                                uses_getters = False
                                data_access = 'node->data'  # default direct access
                                next_access = 'node->next'
                                set_next = 'node->next = nextNode'

                                # Check for getter methods
                                if re.search(r'getData\s*\(\s*\)', genai_content):
                                    uses_getters = True
                                    data_access = 'node->getData()'

                                if re.search(r'getNext\s*\(\s*\)', genai_content):
                                    uses_getters = True
                                    next_access = 'node->getNext()'

                                if re.search(r'setNext\s*\(', genai_content):
                                    set_next = 'node->setNext(nextNode)'

                                # If not using getters, detect actual member names
                                if not uses_getters:
                                    if re.search(r'int\s+val\s*;', genai_content):
                                        data_access = 'node->val'
                                    elif re.search(r'int\s+val_\s*;', genai_content):
                                        data_access = 'node->val_'
                                    elif re.search(r'int\s+data_\s*;', genai_content):
                                        data_access = 'node->data_'
                                    # else default node->data

                                    if re.search(r'Node\s*\*\s*next_\s*;', genai_content):
                                        next_access = 'node->next_'
                                        set_next = 'node->next_ = nextNode'

                                # Check for ListNode vs Node, and whether it's templated
                                node_type = 'Node'
                                is_templated = False
                                if re.search(r'(struct\s+)?ListNode', genai_content):
                                    node_type = 'ListNode'
                                # Check if Node is templated: template <typename T> struct Node
                                if re.search(r'template\s*<\s*typename\s+\w+.*>\s*struct\s+(Node|ListNode)', genai_content):
                                    is_templated = True
                                    node_type = node_type + '<int>'

                                print(f"  Node type detected: {node_type}")
                                print(f"  Data access: {data_access}")
                                print(f"  Next access: {next_access}")
                                print(f"  Set next: {set_next}")

                                merge_func = None
                                class_name = None
                                uses_double_pointer = False  # For void mergeSort(Node** headRef) style
                                uses_reference = False       # For void mergeSort(Node*& head) style

                                # If there's a class, set class_name (we'll use it if we find a method)
                                if class_match:
                                    class_name = class_match.group(1)

                                if merge_func_match:
                                    merge_func = merge_func_match.group(2)
                                    if class_name:
                                        print(f"✓ Found merge sort as class method: {class_name}().{merge_func}()")
                                    else:
                                        print(f"✓ Found merge sort function: {merge_func}")
                                else:
                                    # Try simpler patterns for return-style functions
                                    simple_match = re.search(r'(\w+)\*\s+(mergeSort|merge_sort|sortList)\s*\(', genai_content)
                                    if simple_match:
                                        merge_func = simple_match.group(2)
                                        if class_name:
                                            print(f"✓ Found merge sort as class method: {class_name}().{merge_func}()")
                                        else:
                                            print(f"✓ Found merge sort function: {merge_func}")
                                    else:
                                        # Try void mergeSort(Node** headRef) or void mergeSort(Node<T>** headRef) pattern (modifies in place via double pointer)
                                        void_match = re.search(r'void\s+(mergeSort|merge_sort|sortList)\s*\(\s*(\w+)(?:<\w+>)?\*\*', genai_content)
                                        if void_match:
                                            merge_func = void_match.group(1)
                                            uses_double_pointer = True
                                            if class_name:
                                                print(f"✓ Found merge sort (void, double-pointer) as class method: {class_name}().{merge_func}(&head)")
                                            else:
                                                print(f"✓ Found merge sort function (void, double-pointer): {merge_func}(&head)")
                                        else:
                                            # Try void mergeSort(Node*& head) or void mergeSort(Node<T>*& head) pattern (modifies in place via reference)
                                            ref_match = re.search(r'void\s+(mergeSort|merge_sort|sortList)\s*\(\s*(\w+)(?:<\w+>)?\*\s*&', genai_content)
                                            if ref_match:
                                                merge_func = ref_match.group(1)
                                                uses_reference = True  # Modifies in place via reference (no & needed in call)
                                                if class_name:
                                                    print(f"✓ Found merge sort (void, reference) as class method: {class_name}().{merge_func}(head)")
                                                else:
                                                    print(f"✓ Found merge sort function (void, reference): {merge_func}(head)")
                                            else:
                                                print("✗ Could not find merge sort function - needs manual review")

                                if merge_func:
                                    cwd = os.getcwd()
                                    os.chdir(part3_path)
                                    try:
                                        # Backup GenAI file
                                        genai_backup = "mergeSortGenAI_backup.bak"
                                        shutil.copy2("mergeSortGenAI.cpp", genai_backup)

                                        # Remove main from GenAI file (keep everything else as-is)
                                        with open("mergeSortGenAI.cpp", 'r', encoding='utf-8', errors='ignore') as f:
                                            lines = f.readlines()

                                        main_line = None
                                        for i, line in enumerate(lines):
                                            if 'int main' in line:
                                                main_line = i
                                                break

                                        if main_line is not None:
                                            lines = lines[:main_line]
                                            print(f"✓ Removed main() from GenAI file")

                                        content = ''.join(lines)

                                        with open("mergeSortGenAI.cpp", 'w', encoding='utf-8') as f:
                                            f.write(content)

                                        # Update test main with correct function name, node type, and data member
                                        with open("testMain_GenAI.cpp", 'r', encoding='utf-8') as f:
                                            test_content = f.read()

                                        # Build the function call based on style
                                        if class_name:
                                            if uses_double_pointer:
                                                # void style with double pointer: ClassName().mergeSort(&head)
                                                test_content = test_content.replace(
                                                    'STUDENT_NODE_TYPE* sorted = STUDENT_MERGESORT_FUNC(head);',
                                                    f'STUDENT_NODE_TYPE* sorted = head; {class_name}().{merge_func}(&sorted);'
                                                )
                                            elif uses_reference:
                                                # void style with reference: ClassName().mergeSort(head) - no & needed
                                                test_content = test_content.replace(
                                                    'STUDENT_NODE_TYPE* sorted = STUDENT_MERGESORT_FUNC(head);',
                                                    f'STUDENT_NODE_TYPE* sorted = head; {class_name}().{merge_func}(sorted);'
                                                )
                                            else:
                                                func_call = f'{class_name}().{merge_func}'
                                                test_content = test_content.replace('STUDENT_MERGESORT_FUNC', func_call)
                                        else:
                                            if uses_double_pointer:
                                                # void style with double pointer: mergeSort(&head)
                                                test_content = test_content.replace(
                                                    'STUDENT_NODE_TYPE* sorted = STUDENT_MERGESORT_FUNC(head);',
                                                    f'STUDENT_NODE_TYPE* sorted = head; {merge_func}(&sorted);'
                                                )
                                            elif uses_reference:
                                                # void style with reference: mergeSort(head) - no & needed
                                                test_content = test_content.replace(
                                                    'STUDENT_NODE_TYPE* sorted = STUDENT_MERGESORT_FUNC(head);',
                                                    f'STUDENT_NODE_TYPE* sorted = head; {merge_func}(sorted);'
                                                )
                                            else:
                                                func_call = merge_func
                                                test_content = test_content.replace('STUDENT_MERGESORT_FUNC', func_call)

                                        test_content = test_content.replace('STUDENT_NODE_TYPE', node_type)
                                        test_content = test_content.replace('STUDENT_NODE_DATA', data_access)
                                        test_content = test_content.replace('STUDENT_NODE_NEXT', next_access)
                                        test_content = test_content.replace('STUDENT_NODE_SETNEXT', set_next)

                                        with open("testMain_GenAI.cpp", 'w', encoding='utf-8') as f:
                                            f.write(test_content)

                                        # Compile testMain_GenAI.cpp (it #includes mergeSortGenAI.cpp)
                                        print("\n--- GenAI COMPILATION ---")
                                        try:
                                            with timeout(60):
                                                compile_result = subprocess.run(
                                                    ["g++", "-std=c++20", "-o", "GenAI_test", "testMain_GenAI.cpp"],
                                                    capture_output=True, text=True
                                                )
                                                if compile_result.returncode != 0:
                                                    print(f"✗ Compilation failed:")
                                                    print(compile_result.stderr[:500])
                                                else:
                                                    print("✓ GenAI test compiled")

                                                    print("\n--- GenAI EXECUTION (10 test cases) ---")
                                                    with timeout(30):
                                                        run_executable("GenAI_test")

                                        except TimeoutError:
                                            print("✗ TIMEOUT: GenAI test took too long")

                                    except Exception as e:
                                        print(f"✗ GenAI test failed: {e}")
                                    finally:
                                        # Restore GenAI file
                                        if os.path.exists(genai_backup):
                                            shutil.move(genai_backup, "mergeSortGenAI.cpp")
                                        os.chdir(cwd)

                        else:
                            print("✗ Part3 folder not found")
                        print()

                        # ------------------------------------------------------------
                        # Print LinkedBagDS files (LinkedBag.h and LinkedBag.cpp) for Part 3-2 review
                        # ------------------------------------------------------------
                        linkedbagds_path = os.path.join(fname, 'LinkedBagDS')
                        if not os.path.exists(linkedbagds_path):
                            linkedbagds_path = os.path.join(part3_path, 'LinkedBagDS')

                        if os.path.exists(linkedbagds_path) and os.path.isdir(linkedbagds_path):
                            print("\n" + "="*70)
                            print("LINKEDBAGDS SOURCE FILES (for Part 3-2)")
                            print("="*70)
                            for lb_file in ['LinkedBag.h', 'LinkedBag.cpp']:
                                lb_path = os.path.join(linkedbagds_path, lb_file)
                                if os.path.exists(lb_path):
                                    print(f"\n{'='*70}")
                                    print(f"FILE: {lb_file}")
                                    print('='*70)
                                    try:
                                        with open(lb_path, 'r', encoding='utf-8', errors='ignore') as f:
                                            print(f.read())
                                    except Exception as e:
                                        print(f"Error reading file: {e}")
                                else:
                                    print(f"\n✗ {lb_file} not found")
                        else:
                            print("\n⚠ LinkedBagDS folder not found")
                        print()

                        # ------------------------------------------------------------
                        # Part 3-2: Program Correctness - Main runs (2 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 3-2: Program Correctness - Main runs on terminal (2 pts) ---")

                        part3_compiles = False
                        if os.path.exists(part3_path) and os.path.isdir(part3_path):
                            cwd = os.getcwd()
                            os.chdir(part3_path)
                            try:
                                # Find and backup the student's main file, then replace with test main
                                student_main = None
                                for f in os.listdir('.'):
                                    if 'main' in f.lower() and f.endswith('.cpp') and 'genai' not in f.lower():
                                        student_main = f
                                        break

                                if student_main:
                                    backup_main = student_main + '.bak'
                                    shutil.copy2(student_main, backup_main)
                                    shutil.copy2(TEST_MAIN_LINKEDBAG, student_main)
                                    print(f"✓ Replaced {student_main} with test main")
                                else:
                                    # No main found, just copy our test main
                                    shutil.copy2(TEST_MAIN_LINKEDBAG, 'linkedBagSortingMain.cpp')
                                    print("✓ Copied test main (no existing main found)")

                                print("\n--- PART 3 COMPILATION ---")
                                with timeout(60):
                                    # Exclude GenAI files and other test mains that might be present
                                    o_files = compile_cpp_files(exclude_patterns=[
                                        '*GenAI*',
                                        'testBothSorts*',
                                        'testMain*',
                                        'bubbleSort*',
                                        'insertionSort*',
                                        'selectionSort*',
                                        'heapSort*',
                                        'shellSort*',
                                        'CMake*'
                                    ])
                                    executable_name = "Part3_output"
                                    link_executable(o_files, executable_name)
                                    part3_compiles = True

                                print(f"\n--- PART 3 EXECUTION (MergeSort + QuickSort EC) ---")
                                print(f"Running {executable_name}...")
                                try:
                                    with timeout(30):
                                        run_executable(executable_name)
                                except TimeoutError:
                                    print("✗ TIMEOUT: Execution took too long (possible infinite loop)")

                            except TimeoutError:
                                print("✗ TIMEOUT: Compilation took too long")
                            except Exception as compile_error:
                                print(f"✗ Compilation/Execution failed: {compile_error}")
                            finally:
                                # Restore student's original main
                                if student_main and os.path.exists(backup_main):
                                    shutil.move(backup_main, student_main)
                                os.chdir(cwd)
                        else:
                            print("✗ Part3 folder not found - cannot compile")

                        if part3_compiles:
                            print("\n✓ Part 3 compiles and runs (2 pts)")
                        else:
                            print("\n✗ Part 3 does NOT compile/run (0 pts)")
                        print()

                        # ------------------------------------------------------------
                        # Part 3-2: Program Correctness - Test cases (15 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 3-2: Program Correctness - All test cases correct (15 pts) ---")
                        print("No hard-coding allowed")

                        if os.path.exists(part3_path) and os.path.isdir(part3_path):
                            try:
                                with timeout(30):
                                    check_mergesort_linkedbag(part3_path)
                            except TimeoutError:
                                print("✗ TIMEOUT: LinkedBag merge sort check took too long")
                        print()

                        # ------------------------------------------------------------
                        # Part 3-EC: Quick Sort Style/Docs (2 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 3-EC: Quick Sort Programming Style and Documentation (2 pts EC) ---")

                        if os.path.exists(part3_path) and os.path.isdir(part3_path):
                            try:
                                with timeout(10):
                                    check_quicksort_ec(part3_path, check_style=True)
                            except TimeoutError:
                                print("✗ TIMEOUT: Quick sort EC check took too long")
                        print()

                        # ------------------------------------------------------------
                        # Part 3-EC: Quick Sort Correctness (8 pts)
                        # ------------------------------------------------------------
                        print("\n--- Part 3-EC: Quick Sort Program Correctness (8 pts EC) ---")
                        print("All test cases execute properly with correct output")

                        if os.path.exists(part3_path) and os.path.isdir(part3_path):
                            try:
                                with timeout(10):
                                    check_quicksort_ec(part3_path, check_correctness=True)
                            except TimeoutError:
                                print("✗ TIMEOUT: Quick sort EC check took too long")
                        print()

                        # ============================================================
                        # FILE STRUCTURE
                        # ============================================================
                        print("\n" + "-"*70)
                        print("FILE STRUCTURE")
                        print("-"*70)

                        print("\nTop-level directory listing:")
                        try:
                            for item in os.listdir(fname):
                                item_path = os.path.join(fname, item)
                                if os.path.isdir(item_path):
                                    print(f"  [DIR] {item}/")
                                else:
                                    print(f"  {item}")
                        except Exception as e:
                            print(f"Error listing directory: {e}")

                        # Check Part1 structure
                        if os.path.exists(part1_path) and os.path.isdir(part1_path):
                            print(f"\nPart1/ directory listing:")
                            for item in os.listdir(part1_path):
                                print(f"  {item}")

                        # Check Part3 structure
                        if os.path.exists(part3_path) and os.path.isdir(part3_path):
                            print(f"\nPart3/ directory listing:")
                            for item in os.listdir(part3_path):
                                item_path = os.path.join(part3_path, item)
                                if os.path.isdir(item_path):
                                    print(f"  [DIR] {item}/")
                                else:
                                    print(f"  {item}")

                        # ============================================================
                        # SOURCE FILE CONTENTS - Part1
                        # ============================================================
                        if os.path.exists(part1_path) and os.path.isdir(part1_path):
                            print("\n" + "="*70)
                            print("PART 1 SOURCE FILES")
                            print("="*70)
                            print_source_files(part1_path)

                        # ============================================================
                        # SOURCE FILE CONTENTS - Part3
                        # ============================================================
                        if os.path.exists(part3_path) and os.path.isdir(part3_path):
                            print("\n" + "="*70)
                            print("PART 3 SOURCE FILES")
                            print("="*70)
                            print_source_files(part3_path)

                        # LinkedBagDS files already printed earlier after Part 3-1

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

    print(f"Grading complete. Output written to {log_file}")
