import glob
import subprocess

def compile_cpp_files():
    cpp_files = glob.glob("*.cpp")
    if not cpp_files:
        raise FileNotFoundError("No .cpp files found in current folder")
    print("\n--- Compiling: ---\n", cpp_files)
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

def link_executable(o_files, executable_name):
    result = subprocess.run(["g++", "-o", executable_name] + o_files,
                            capture_output=True, text=True)
    print(result.stdout, end='')
    print(result.stderr, end='')
    if result.returncode != 0:
        raise RuntimeError("Linking failed")
    return executable_name

def run_executable(executable_name):
    result = subprocess.run([f"./{executable_name}"], capture_output=True, text=True)
    print(result.stdout, end='')
    print(result.stderr, end='')
