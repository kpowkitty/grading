import glob
import subprocess
import fnmatch

def compile_cpp_files(exclude_patterns=None):
    cpp_files = glob.glob("*.cpp")
    if exclude_patterns:
        for pattern in exclude_patterns:
            cpp_files = [f for f in cpp_files if not fnmatch.fnmatch(f, pattern)]
    if not cpp_files:
        raise FileNotFoundError("No .cpp files found in current folder")
    print("\n--- Compiling: ---\n", cpp_files)
    result = subprocess.run(["g++", "-std=c++20", "-c"] + cpp_files,
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


def run_executable(executable_name, timeout_seconds=5):
    """
    Run executable with timeout and capture output.
    Works for both interactive and non-interactive programs.
    
    Args:
        executable_name: Name of executable to run
        timeout_seconds: Max seconds to let it run (default 5)
    
    Returns:
        bool: True if executable started, False if failed
    """
    try:
        process = subprocess.Popen(
            [f'./{executable_name}'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            # Try to run for timeout_seconds
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            if process.returncode == 0:
                print(f"✓ Executable ran and completed (exit code: {process.returncode})")
            elif process.returncode < 0:
                # Negative return code means killed by signal (e.g., -11 = SIGSEGV)
                import signal
                sig_num = -process.returncode
                sig_name = signal.Signals(sig_num).name if sig_num in signal.Signals._value2member_map_ else f"signal {sig_num}"
                print(f"✗ Executable CRASHED ({sig_name}, exit code: {process.returncode})")
            else:
                print(f"✗ Executable failed (exit code: {process.returncode})")
            if stdout:
                print("\n--- Program Output ---")
                print(stdout[:10000])  # First 10000 chars
                print("--- End Output ---\n")
            if stderr:
                print("\n--- Errors ---")
                print(stderr[:1000])
                print("--- End Errors ---\n")
            return True
            
        except subprocess.TimeoutExpired:
            # Program still running after timeout - kill it and get output
            process.kill()
            stdout, stderr = process.communicate()
            print(f"✓ Executable started (timed out after {timeout_seconds}s - likely waiting for input)")
            if stdout:
                print("\n--- Program Output (before timeout) ---")
                print(stdout[:10000])
                print("--- End Output ---\n")
            if stderr:
                print("\n--- Errors (before timeout) ---")
                print(stderr[:1000])
                print("--- End Errors ---\n")
            return True
        
    except FileNotFoundError:
        print(f"✗ Executable not found: {executable_name}")
        return False
    except Exception as e:
        print(f"✗ Execution failed: {e}")
        return False
