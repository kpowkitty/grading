import os
import shutil
import zipfile
import glob
import subprocess
import filecmp
import sys
import difflib
from pathlib import Path

class Grader:
    def __init__(self, submissions_folder="submissions_unzip",
                 test_files_folder="testing_files",
                 testcases_filename="test_cases.txt"):
        self.root_folder = str(Path(__file__).resolve().parent)
        self.submissions_folder = os.path.join(self.root_folder, submissions_folder)
        self.test_files_folder = os.path.join(self.root_folder, test_files_folder)
        self.testcases_filename = testcases_filename
        self.required_program_files = ["myLibrary.hpp", "myLibrary.cpp", "testing.cpp"]

    def prepare_submissions_folder(self):
        """Extract submissions.zip into submissions_folder."""
        os.makedirs(self.submissions_folder, exist_ok=True)
        zip_path = os.path.join(self.root_folder, "submissions.zip")
        if not os.path.exists(zip_path):
            downloads_zip = os.path.join(Path.home(), "Downloads", "submissions.zip")
            if os.path.exists(downloads_zip):
                shutil.copy(downloads_zip, self.root_folder)
                print(f"Copied submissions.zip from Downloads to {self.root_folder}")
            else:
                raise FileNotFoundError("submissions.zip not found")
        print("Extracting submissions.zip...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.submissions_folder)
        print("Extraction complete.")

    def unzip_submission(self, zip_file):
        fname = os.path.splitext(zip_file)[0]
        os.makedirs(fname, exist_ok=True)
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(fname)
        return fname

    def flatten_inner_folder(self, fname):
        cpp_files = glob.glob(os.path.join(fname, '*.cpp'))
        if cpp_files:
            return
        inner_folder = next((d for d in os.listdir(fname) if os.path.isdir(os.path.join(fname, d))), None)
        if inner_folder:
            inner_folder_path = os.path.join(fname, inner_folder)
            for item in os.listdir(inner_folder_path):
                shutil.move(os.path.join(inner_folder_path, item), fname)

 
    def move_test_files(self, fname):
        """Ensure test files exist and are correct; handle differences according to rules."""
        required_files = ["mainProgram.cpp", "testing.cpp", "testing.hpp", "test_cases.txt"]
        for file_name in required_files:
            student_file = os.path.join(fname, file_name)
            standard_file = os.path.join(self.test_files_folder, file_name)
    
            if not os.path.exists(student_file):
                shutil.copy(standard_file, fname)
            else:
                # Handle normal code files (except test_cases.txt)
                if file_name != "test_cases.txt" and not filecmp.cmp(student_file, standard_file, shallow=False):
                    print(f"\n--- Differences in {file_name} ---")
                    diff_lines = difflib.unified_diff(
                        open(standard_file).readlines(),
                        open(student_file).readlines(),
                        fromfile='standard',
                        tofile='student',
                    )
                    diff_output = "".join(diff_lines)
                    print(diff_output)
                    print(f"--- End of differences in {file_name} ---\n")
                    shutil.copy(standard_file, fname)
    
                # Always ensure test_cases.txt matches standard version quietly
                elif file_name == "test_cases.txt" and not filecmp.cmp(student_file, standard_file, shallow=False):
                    shutil.copy(standard_file, fname)


    def compile_cpp_files(self):
        cpp_files = glob.glob("*.cpp")
        if not cpp_files:
            raise FileNotFoundError("No .cpp files found in current folder")
        print("Compiling:", cpp_files)
        result = subprocess.run(["g++", "-std=c++11", "-c"] + cpp_files,
                                capture_output=True, text=True)
        print(result.stdout, end='')
        print(result.stderr, end='')
        if result.returncode != 0:
            raise RuntimeError("Compilation failed")
        o_files = glob.glob("*.o")
        if not o_files:
            raise RuntimeError("No object files generated after compilation")
        return o_files

    def link_executable(self, o_files, executable_name):
        result = subprocess.run(["g++", "-o", executable_name] + o_files,
                                capture_output=True, text=True)
        print(result.stdout, end='')
        print(result.stderr, end='')
        if result.returncode != 0:
            raise RuntimeError("Linking failed")
        return executable_name

    def run_executable(self, executable_name):
        result = subprocess.run([f"./{executable_name}"], capture_output=True, text=True)
        print(result.stdout, end='')
        print(result.stderr, end='')

    def check_program_design(self, fname):
        print("\n--- Program Design Check ---")
        for req_file in self.required_program_files:
            path = os.path.join(fname, req_file)
            if os.path.exists(path):
                print(f"{req_file}: SUCCESS")
            else:
                print(f"{req_file}: FAILURE")
        print("\n--- Current directory listing ---")
        for file in os.listdir(fname):
            print(file)


    def print_library_files(self, fname):
        print("\n--- Student Library Files ---")
        for lib_file in ["myLibrary.hpp", "myLibrary.cpp"]:
            path = os.path.join(fname, lib_file)
            if os.path.exists(path):
                print(f"\n--- {lib_file} ---")
                with open(path, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print(f"{lib_file} not found!")


    

    def grade_submission(self, zip_file):
        print(f"\n-------------------------------------------------------   Processing: {zip_file}")
        
        # Handle if it's already extracted (directory with .zip suffix)
        if os.path.isdir(zip_file):
            fname = zip_file
        else:
            fname = self.unzip_submission(zip_file)
        
        self.flatten_inner_folder(fname)
        self.print_library_files(fname)
        self.check_program_design(fname)
        self.move_test_files(fname)

    
        # 4. Compile, link, and run (change dir only for compilation/run)
        cwd = os.getcwd()
        os.chdir(fname)
        try:
            try:
                o_files = self.compile_cpp_files()
                executable_name = f"{Path(fname).name}_output"
                self.link_executable(o_files, executable_name)
                self.run_executable(executable_name)
            except Exception as e:
                print(f"Compilation/Execution error: {e}")
        finally:
            os.chdir(cwd)



    def grade_all_submissions(self):
        self.prepare_submissions_folder()
        os.chdir(self.submissions_folder)
        entries = glob.glob("*.zip")
        entries += [d for d in os.listdir(".") if d.endswith(".zip") and os.path.isdir(d)]
        
        for entry in entries:
            try:
                self.grade_submission(entry)
                print(f"Completed: {entry}\n")
            except Exception as e:
                print(f"Error processing {entry}: {e}\n")


if __name__ == "__main__":
    log_file = "grading_output.txt"
    with open(log_file, "w", encoding="utf-8") as f:
        # Redirect stdout/stderr to log file
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = f
        sys.stderr = f
        try:
            grader = Grader()
            grader.grade_all_submissions()
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
    print(f"Grading complete. Output written to {log_file}")

