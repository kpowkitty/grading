import os
from .utils import log_diff
import filecmp
import shutil

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
