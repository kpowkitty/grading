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
    
    Args:
        folder_path: Path to folder containing source files
    """
    print("\n" + "="*70)
    print("SOURCE FILE CONTENTS")
    print("="*70)
    
    # Get all .h and .cpp files
    files = [f for f in os.listdir(folder_path) 
             if f.endswith('.h') or f.endswith('.cpp')]
    
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
