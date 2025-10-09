import difflib

def log_diff(student_file, standard_file, file_name):
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
