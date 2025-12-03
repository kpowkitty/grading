import os
import re
from .utils import log_diff
from pathlib import Path
import filecmp
import shutil
from typing import Dict, List, Tuple, Set

def check_program_design(fname, required_program_files):
    print("\n--- Program Design Check ---")
    for req_file in required_program_files:
        path = os.path.join(fname, req_file)
        print(f"{req_file}: {'SUCCESS' if os.path.exists(path) else 'FAILURE'}")

    print("\n--- Current directory listing ---")
    for file in os.listdir(fname):
        print(file)


def print_library_files(fname):
    print("\n--- Student Library Files ---")
    for lib_file in ["myLibrary.hpp", "myLibrary.cpp"]:
        path = os.path.join(fname, lib_file)
        if os.path.exists(path):
            print(f"\n--- {lib_file} ---")
            with open(path, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print(f"{lib_file} not found!")


def move_test_files(fname, test_files_folder):
    required_files = ["mainProgram.cpp", "testing.cpp", "testing.hpp", "test_cases.txt"]
    for file_name in required_files:
        student_file = os.path.join(fname, file_name)
        standard_file = os.path.join(test_files_folder, file_name)

        if not os.path.exists(student_file):
            shutil.copy(standard_file, fname)
        else:
            if file_name != "test_cases.txt" and not filecmp.cmp(student_file, standard_file, shallow=False):
                log_diff(student_file, standard_file, file_name)
                shutil.copy(standard_file, fname)
            elif file_name == "test_cases.txt" and not filecmp.cmp(student_file, standard_file, shallow=False):
                shutil.copy(standard_file, fname)


def check_class_files_exist(folder_path: str, class_names: List[str]) -> Dict[str, bool]:
    """
    Check if class files (.h and .cpp) exist for given class names.
    
    Args:
        folder_path: Path to folder containing source files
        class_names: List of class names to check for
        
    Returns:
        Dict mapping class name to whether both .h and .cpp exist
    """
    results = {}
    files = os.listdir(folder_path)
    
    for class_name in class_names:
        # Check various naming conventions
        possible_names = [
            class_name,
            class_name.lower(),
        ]
        
        has_header = False
        has_cpp = False
        
        for name in possible_names:
            if any(f.startswith(name) and f.endswith('.h') for f in files):
                has_header = True
            
            if any(f.startswith(name) and f.endswith('.cpp') for f in files):
                has_cpp = True
        
        results[class_name] = has_header and has_cpp
        
        if has_header and has_cpp:
            print(f"✓ {class_name}: Found both .h and .cpp files")
        else:
            print(f"✗ {class_name}: Missing files (header: {has_header}, cpp: {has_cpp})")
    
    return results


def find_inheritance(folder_path: str) -> List[tuple]:
    """
    Find inheritance relationships in header files.
    
    Args:
        folder_path: Path to folder containing source files
        
    Returns:
        List of tuples: (derived_class, base_class, filename)
    """
    header_files = [f for f in os.listdir(folder_path) if f.endswith('.h')]
    
    inheritance_found = []
    inheritance_pattern = re.compile(r'class\s+(\w+)\s*:\s*public\s+(\w+)')
    
    for file in header_files:
        try:
            with open(os.path.join(folder_path, file), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = inheritance_pattern.findall(content)
                for derived, base in matches:
                    inheritance_found.append((derived, base, file))
                    print(f"✓ Found inheritance: {derived} : public {base} in {file}")
        except Exception as e:
            print(f"Warning: Could not read {file}: {e}")
    
    if not inheritance_found:
        print("✗ No inheritance found")
    
    return inheritance_found


def check_function_exists_in_file(folder_path: str, filename_pattern: str, 
                                   function_names: List[str]) -> Dict[str, bool]:
    """
    Check if functions exist in files matching a pattern.
    
    Args:
        folder_path: Path to folder containing source files
        filename_pattern: Pattern to match filenames (e.g., 'linkedbag')
        function_names: List of function names to search for
        
    Returns:
        Dict mapping function name to whether it was found
    """
    matching_files = []
    
    # Find matching files (could be in subfolder)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if filename_pattern.lower() in file.lower() and file.endswith('.cpp'):
                matching_files.append(os.path.join(root, file))
    
    results = {func: False for func in function_names}
    
    if not matching_files:
        print(f"✗ No files matching '{filename_pattern}' found")
        return results
    
    for file in matching_files:
        print(f"Checking {file} for functions...")
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for func in function_names:
                    if func in content:
                        results[func] = True
                        print(f"✓ Found {func} in file")
        except Exception as e:
            print(f"Warning: Could not read {file}: {e}")
    
    for func, found in results.items():
        if not found:
            print(f"✗ {func} not found")
    
    return results


def check_function_usage(folder_path: str, function_names: List[str]) -> Dict[str, bool]:
    """
    Check if functions are called/used in any .cpp files.
    
    Args:
        folder_path: Path to folder containing source files
        function_names: List of function names to search for usage
        
    Returns:
        Dict mapping function name to whether usage was found
    """
    cpp_files = [f for f in os.listdir(folder_path) if f.endswith('.cpp')]
    
    usage_found = {func: False for func in function_names}
    
    for file in cpp_files:
        try:
            with open(os.path.join(folder_path, file), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for func in function_names:
                    # Look for function calls (basic pattern)
                    if re.search(rf'\b{func}\s*\(', content):
                        usage_found[func] = True
                        print(f"✓ Found usage of {func} in {file}")
        except Exception as e:
            print(f"Warning: Could not read {file}: {e}")
    
    for func, found in usage_found.items():
        if not found:
            print(f"✗ No usage of {func} found")
    
    return usage_found


def count_pattern_in_files(folder_path: str, filename_pattern: str, 
                           search_pattern: str) -> int:
    """
    Count occurrences of a regex pattern in files matching filename pattern.
    
    Args:
        folder_path: Path to folder containing source files
        filename_pattern: Pattern to match filenames (e.g., 'organizer')
        search_pattern: Regex pattern to search for
        
    Returns:
        Count of pattern occurrences
    """
    matching_files = [f for f in os.listdir(folder_path) 
                      if filename_pattern.lower() in f.lower() and 
                      (f.endswith('.h') or f.endswith('.cpp'))]
    
    if not matching_files:
        print(f"✗ No files matching '{filename_pattern}' found")
        return 0
    
    total_count = 0
    
    for file in matching_files:
        try:
            with open(os.path.join(folder_path, file), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = re.findall(search_pattern, content)
                count = len(matches)
                total_count += count
                
                if count > 0:
                    print(f"Found {count} occurrence(s) in {file}")
        except Exception as e:
            print(f"Warning: Could not read {file}: {e}")
    
    return total_count


def check_keyword_in_files(folder_path: str, filename_pattern: str, 
                           keywords: List[str]) -> Dict[str, bool]:
    """
    Check if keywords/patterns exist in files matching filename pattern.
    
    Args:
        folder_path: Path to folder containing source files
        filename_pattern: Pattern to match filenames (e.g., 'main')
        keywords: List of regex patterns to search for
        
    Returns:
        Dict mapping keyword to whether it was found
    """
    matching_files = [f for f in os.listdir(folder_path) 
                      if filename_pattern.lower() in f.lower() and f.endswith('.cpp')]
    
    if not matching_files:
        # Try all .cpp files if no match
        matching_files = [f for f in os.listdir(folder_path) if f.endswith('.cpp')]
    
    results = {kw: False for kw in keywords}
    
    for file in matching_files:
        try:
            with open(os.path.join(folder_path, file), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                
                for keyword in keywords:
                    if re.search(keyword.lower(), content):
                        results[keyword] = True
        except Exception as e:
            print(f"Warning: Could not read {file}: {e}")
    
    return results


def check_files_exist(folder_path: str, filenames: List[str]) -> Dict[str, bool]:
    """
    Check if specific files exist in folder.
    
    Args:
        folder_path: Path to folder to check
        filenames: List of filenames to look for
        
    Returns:
        Dict mapping filename to whether it exists
    """
    files = os.listdir(folder_path)
    results = {}
    
    for filename in filenames:
        exists = filename in files
        results[filename] = exists
        
        if exists:
            print(f"✓ Found {filename}")
        else:
            print(f"✗ {filename} not found")
    
    return results


def print_source_files(folder_path: str):
    """
    Print contents of all .h and .cpp files in folder.
    Skips CMake files, CLion files, and dotfiles.

    Args:
        folder_path: Path to folder containing source files
    """
    print("\n" + "="*70)
    print("SOURCE FILE CONTENTS")
    print("="*70)

    # Patterns to skip
    skip_patterns = [
        'cmake',           # CMake files
        'cmakelist',       # CMakeLists
        '.cmake',          # .cmake extension in name
        'clion',           # CLion files
    ]

    def should_skip(filename):
        # Skip dotfiles (includes ._ Mac metadata files)
        if filename.startswith('.'):
            return True
        # Skip Mac resource fork files (._filename)
        if filename.startswith('._'):
            return True
        # Skip files matching skip patterns (case-insensitive)
        lower_name = filename.lower()
        for pattern in skip_patterns:
            if pattern in lower_name:
                return True
        return False

    # Get all .h and .cpp files, excluding skipped patterns
    files = [f for f in os.listdir(folder_path)
             if (f.endswith('.h') or f.endswith('.cpp')) and not should_skip(f)]

    # Sort: headers first, then cpp
    headers = sorted([f for f in files if f.endswith('.h')])
    cpp_files = sorted([f for f in files if f.endswith('.cpp')])
    all_files = headers + cpp_files
    
    if not all_files:
        print("No .h or .cpp files found")
        return
    
    for file in all_files:
        print(f"\n{'='*70}")
        print(f"FILE: {file}")
        print('='*70)
        try:
            with open(os.path.join(folder_path, file), 'r', 
                     encoding='utf-8', errors='ignore') as f:
                content = f.read()
                print(content)
        except Exception as e:
            print(f"Error reading file: {e}")
    
    print(f"\n{'='*70}")
    print(f"END OF SOURCE FILES")
    print('='*70 + "\n")


def check_smart_pointers(folder_path: str, print_files: bool = True) -> Dict[str, any]:
    """
    Check for smart pointer usage in the codebase.

    Checks for:
    - LinkedBag of pointers
    - Use of smart pointers (shared_ptr, unique_ptr, make_shared, make_unique)
    - Polymorphism with smart pointers

    Args:
        folder_path: Path to folder containing source files
        print_files: Whether to print relevant file contents

    Returns:
        Dict with results of smart pointer checks
    """
    results = {
        'linkedbag_of_pointers': False,
        'smart_pointer_types': [],
        'smart_pointer_creation': [],
        'polymorphism_detected': False
    }

    # Track which files had matches and what lines matched
    matched_lines = {}  # filename -> list of (check_type, line)

    # Get all source files
    source_files = []
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if f.endswith('.cpp') or f.endswith('.h'):
                source_files.append(os.path.join(root, f))

    print("Checking for smart pointer usage...")

    # Store Organizer.cpp content in case we need to print it
    organizer_content = None

    for file_path in source_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                filename = os.path.basename(file_path)

                # Store Organizer.cpp content
                if 'organizer' in filename.lower() and filename.endswith('.cpp'):
                    organizer_content = content

                # Check for LinkedBag of pointers
                match = re.search(r'.*LinkedBag\s*<\s*(\w+::)?(shared_ptr|unique_ptr|[\w]+\s*\*).*', content)
                if match:
                    results['linkedbag_of_pointers'] = True
                    print(f"✓ Found LinkedBag of pointers in {filename}")
                    if filename not in matched_lines:
                        matched_lines[filename] = []
                    # Find the actual line
                    for line in content.split('\n'):
                        if re.search(r'LinkedBag\s*<\s*(\w+::)?(shared_ptr|unique_ptr|[\w]+\s*\*)', line):
                            matched_lines[filename].append(('LinkedBag of pointers', line.strip()))
                            break

                # Check for smart pointer type usage
                for ptr_type in ['shared_ptr', 'unique_ptr']:
                    if ptr_type in content:
                        if ptr_type not in results['smart_pointer_types']:
                            results['smart_pointer_types'].append(ptr_type)
                            print(f"✓ Found {ptr_type} usage in {filename}")
                            if filename not in matched_lines:
                                matched_lines[filename] = []
                            # Find example line
                            for line in content.split('\n'):
                                if ptr_type in line:
                                    matched_lines[filename].append((f'{ptr_type} usage', line.strip()))
                                    break

                # Check for smart pointer creation
                for creation in ['make_shared', 'make_unique']:
                    if creation in content:
                        if creation not in results['smart_pointer_creation']:
                            results['smart_pointer_creation'].append(creation)
                            print(f"✓ Found {creation} usage in {filename}")
                            if filename not in matched_lines:
                                matched_lines[filename] = []
                            # Find example line
                            for line in content.split('\n'):
                                if creation in line:
                                    matched_lines[filename].append((f'{creation} usage', line.strip()))
                                    break

                # Check for polymorphism patterns (base pointer to derived)
                if re.search(r'(std\s*::\s*)?(shared_ptr|unique_ptr)\s*<\s*(Event|EventTicket340)\s*>', content):
                    if re.search(r'(VirtualEvent|VenueEvent)', content):
                        results['polymorphism_detected'] = True
                        print(f"✓ Polymorphism pattern detected in {filename}")
                        if filename not in matched_lines:
                            matched_lines[filename] = []
                        matched_lines[filename].append(('Polymorphism', 'Base pointer with derived types'))

        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")

    # Summary of failures
    any_failure = False
    if not results['linkedbag_of_pointers']:
        print("✗ LinkedBag of pointers not found")
        any_failure = True
    if not results['smart_pointer_types']:
        print("✗ No smart pointer types found")
        any_failure = True
    if not results['smart_pointer_creation']:
        print("✗ No smart pointer creation (make_shared/make_unique) found")
        any_failure = True
    if not results['polymorphism_detected']:
        print("⚠ Polymorphism with smart pointers not clearly detected")
        any_failure = True

    # Print matched lines for successes
    if print_files and matched_lines:
        print(f"\n{'-'*50}")
        print("MATCHED SMART POINTER LINES")
        print(f"{'-'*50}")
        for filename, lines in matched_lines.items():
            print(f"\n{filename}:")
            for check_type, line in lines:
                print(f"  [{check_type}] {line}")

    # If any check failed, print Organizer.cpp
    if print_files and any_failure:
        print(f"\n{'-'*50}")
        print("Organizer.cpp (for manual review)")
        print(f"{'-'*50}")
        if organizer_content:
            print(organizer_content)
        else:
            print("(Organizer.cpp not found)")

    return results


def check_friend_operator_overload(folder_path: str, class_name: str,
                                    operators: List[str],
                                    print_files: bool = True) -> Dict[str, bool]:
    """
    Check if friend operator overloads are implemented for a class.

    Args:
        folder_path: Path to folder containing source files
        class_name: Name of the class to check
        operators: List of operators to check (e.g., ['<<', '>>'])
        print_files: Whether to print matched lines or full files on failure

    Returns:
        Dict mapping operator to whether it was found
    """
    results = {op: False for op in operators}
    matched_lines = {}  # op -> (filename, line)
    file_contents = {}  # filename -> content

    # Find matching files (skip Mac metadata files)
    matching_files = []
    for f in os.listdir(folder_path):
        if f.startswith('._'):
            continue
        if class_name.lower() in f.lower() and (f.endswith('.cpp') or f.endswith('.h')):
            matching_files.append(f)

    if not matching_files:
        print(f"✗ No files found for class {class_name}")
        return results

    for file in matching_files:
        try:
            with open(os.path.join(folder_path, file), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                file_contents[file] = content

                for op in operators:
                    if results[op]:  # Already found this operator
                        continue

                    # Check for friend declaration or implementation
                    # Pattern: friend ... operator<< or operator<<
                    escaped_op = re.escape(op)
                    patterns = [
                        rf'friend\s+.*operator\s*{escaped_op}',
                        rf'operator\s*{escaped_op}\s*\([^)]*{class_name}',
                        rf'ostream\s*&\s*operator\s*{escaped_op}',
                        rf'istream\s*&\s*operator\s*{escaped_op}'
                    ]

                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            results[op] = True
                            # Find the matching line
                            for line in content.split('\n'):
                                if re.search(pattern, line, re.IGNORECASE):
                                    matched_lines[op] = (file, line.strip())
                                    break
                            break

        except Exception as e:
            print(f"Warning: Could not read {file}: {e}")

    # Print results
    any_failure = False
    for op, found in results.items():
        if found:
            print(f"✓ {class_name}: operator{op} found")
        else:
            print(f"✗ {class_name}: operator{op} not found")
            any_failure = True

    # Print matched lines for successes
    if print_files and matched_lines:
        print(f"\n  Matched lines:")
        for op, (filename, line) in matched_lines.items():
            print(f"    [operator{op}] {filename}: {line}")

    # If any operator not found, print the class files
    if print_files and any_failure and file_contents:
        print(f"\n{'-'*50}")
        print(f"{class_name} FILES (for manual review)")
        print(f"{'-'*50}")
        # Sort: headers first
        filenames = list(file_contents.keys())
        headers = sorted([f for f in filenames if f.endswith('.h')])
        cpp_files = sorted([f for f in filenames if f.endswith('.cpp')])
        for filename in headers + cpp_files:
            print(f"\n--- {filename} ---")
            print(file_contents[filename])
            print(f"--- END {filename} ---")

    return results


def check_big3_implementation(folder_path: str, class_name: str,
                              print_files: bool = True) -> Dict[str, bool]:
    """
    Check if the Big 3 (destructor, copy constructor, copy assignment) are implemented.

    Args:
        folder_path: Path to folder containing source files
        class_name: Name of the class to check
        print_files: Whether to print the class file contents after checking

    Returns:
        Dict with 'destructor', 'copy_constructor', 'copy_assignment' keys
    """
    results = {
        'destructor': False,
        'copy_constructor': False,
        'copy_assignment': False
    }

    # Find matching files (skip Mac metadata files)
    matching_files = []
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if f.startswith('._'):
                continue
            if class_name.lower() in f.lower() and (f.endswith('.cpp') or f.endswith('.h')):
                matching_files.append(os.path.join(root, f))

    if not matching_files:
        print(f"✗ No files found for class {class_name}")
        return results

    file_contents = {}  # Store contents for printing later

    for file_path in matching_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                filename = os.path.basename(file_path)
                file_contents[filename] = content

                # Check for destructor: ~ClassName
                if re.search(rf'~\s*{class_name}\s*\(', content):
                    results['destructor'] = True

                # Check for copy constructor: ClassName(const ClassName&) or ClassName(ClassName&)
                if re.search(rf'{class_name}\s*\(\s*(const\s+)?{class_name}\s*&', content):
                    results['copy_constructor'] = True

                # Check for copy assignment operator: operator=(const ClassName&) or operator=(ClassName&)
                if re.search(rf'operator\s*=\s*\(\s*(const\s+)?{class_name}\s*&', content):
                    results['copy_assignment'] = True

        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")

    # Print results
    print(f"\n{class_name} Big 3 check:")
    if results['destructor']:
        print(f"  ✓ Destructor (~{class_name}) found")
    else:
        print(f"  ✗ Destructor (~{class_name}) not found")

    if results['copy_constructor']:
        print(f"  ✓ Copy constructor found")
    else:
        print(f"  ✗ Copy constructor not found")

    if results['copy_assignment']:
        print(f"  ✓ Copy assignment operator (operator=) found")
    else:
        print(f"  ✗ Copy assignment operator (operator=) not found")

    # Print file contents if requested
    if print_files and file_contents:
        print_class_files(class_name, file_contents)

    return results


def print_class_files(class_name: str, file_contents: Dict[str, str]):
    """
    Print the contents of class files.

    Args:
        class_name: Name of the class (for header)
        file_contents: Dict mapping filename to content
    """
    print(f"\n{'-'*50}")
    print(f"{class_name} FILE CONTENTS")
    print(f"{'-'*50}")

    # Sort: headers first, then cpp (skip Mac metadata files)
    filenames = [f for f in file_contents.keys() if not f.startswith('._')]
    headers = sorted([f for f in filenames if f.endswith('.h')])
    cpp_files = sorted([f for f in filenames if f.endswith('.cpp')])
    sorted_files = headers + cpp_files

    for filename in sorted_files:
        print(f"\n--- {filename} ---")
        print(file_contents[filename])
        print(f"--- END {filename} ---")


def check_linkedbag_operator_overload(folder_path: str) -> bool:
    """
    Check if LinkedBag has operator= overloaded.
    Looks in LinkedBagDS folder or linkedbag files.

    Returns:
        True if operator= is found in LinkedBag
    """
    print("\nChecking LinkedBag operator= overload...")

    # Search in LinkedBagDS folder and root
    search_paths = [folder_path]
    linkedbag_dir = os.path.join(folder_path, 'LinkedBagDS')
    if os.path.exists(linkedbag_dir) and os.path.isdir(linkedbag_dir):
        search_paths.append(linkedbag_dir)

    found_header = False
    found_impl = False

    for search_path in search_paths:
        if not os.path.exists(search_path) or not os.path.isdir(search_path):
            continue

        for f in os.listdir(search_path):
            # Skip if not a linkedbag file
            if 'linkedbag' not in f.lower():
                continue

            # Skip directories and non-source files
            file_path = os.path.join(search_path, f)
            if os.path.isdir(file_path):
                continue
            if not (f.endswith('.h') or f.endswith('.cpp')):
                continue
            # Skip Mac metadata files
            if f.startswith('._'):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()

                    # Check for operator= in header (.h file)
                    if f.endswith('.h'):
                        if re.search(r'LinkedBag\s*<[^>]+>\s*&\s*operator\s*=', content):
                            found_header = True
                            print(f"  ✓ operator= prototype found in {f}")

                    # Check for operator= implementation (.cpp file)
                    if f.endswith('.cpp'):
                        if re.search(r'LinkedBag\s*<[^>]+>\s*&\s*LinkedBag\s*<[^>]+>\s*::\s*operator\s*=', content):
                            found_impl = True
                            print(f"  ✓ operator= implementation found in {f}")
                        elif re.search(r'operator\s*=\s*\(\s*(const\s+)?LinkedBag', content):
                            found_impl = True
                            print(f"  ✓ operator= implementation found in {f}")

            except Exception as e:
                print(f"Warning: Could not read {f}: {e}")

    if found_header and found_impl:
        print("✓ LinkedBag operator= correctly overloaded (header + implementation)")
        return True
    elif found_header:
        print("⚠ LinkedBag operator= prototype found but implementation may be missing")
        return True
    elif found_impl:
        print("⚠ LinkedBag operator= implementation found but prototype may be missing")
        return True
    else:
        print("✗ LinkedBag operator= not found")
        return False


def check_test_case_files(folder_path: str) -> Dict[str, bool]:
    """
    Check for non-trivial test case files.

    Returns:
        Dict with test file findings
    """
    results = {
        'has_input_file': False,
        'has_output_file': False,
        'input_files': [],
        'output_files': []
    }

    print("\nChecking for test case files...")

    for f in os.listdir(folder_path):
        f_lower = f.lower()

        # Check for input files
        if 'input' in f_lower or f_lower.startswith('in'):
            if f.endswith('.txt'):
                results['has_input_file'] = True
                results['input_files'].append(f)
                print(f"  ✓ Found input file: {f}")

        # Check for output files
        if 'output' in f_lower or f_lower.startswith('out') or 'expected' in f_lower:
            if f.endswith('.txt'):
                results['has_output_file'] = True
                results['output_files'].append(f)
                print(f"  ✓ Found output file: {f}")

    if not results['has_input_file']:
        print("  ✗ No input test file found")
    if not results['has_output_file']:
        print("  ✗ No output/expected file found")

    return results
