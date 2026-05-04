import difflib
import os
import shutil
import fnmatch


def organize_flat_submission(base_path, dirs, file_mappings, dir_mappings=None):
    """
    Organize a flat submission into directories if they don't exist.

    Args:
        base_path: Path to the submission root
        dirs: List of directory names that should exist (e.g., ['Part1', 'Part3'])
        file_mappings: List of lists - file_mappings[i] contains file patterns for dirs[i]
                       Use '*' to mean "everything else remaining"
        dir_mappings: Optional list of lists - dir_mappings[i] contains subdirectory names
                      that should be moved into dirs[i] (e.g., [[], ['LinkedBagDS']])

    Example:
        organize_flat_submission(path,
            ['Part1', 'Part3'],
            [['seriesRecursive.cpp'], ['*']],
            [[], ['LinkedBagDS']]
        )
        This puts seriesRecursive.cpp in Part1, everything else + LinkedBagDS/ in Part3.

    Returns:
        True if reorganization was performed, False if dirs already existed
    """
    # Check if all directories already exist
    all_exist = all(os.path.isdir(os.path.join(base_path, d)) for d in dirs)
    if all_exist:
        return False

    # Get list of files in base_path (not directories)
    files = [f for f in os.listdir(base_path)
             if os.path.isfile(os.path.join(base_path, f))]

    # Get list of subdirectories in base_path (excluding target dirs)
    subdirs = [d for d in os.listdir(base_path)
               if os.path.isdir(os.path.join(base_path, d)) and d not in dirs]

    if not files and not subdirs:
        return False

    print(f"  Reorganizing flat submission into {dirs}...")

    # Track which files/dirs have been moved
    moved_files = set()
    moved_dirs = set()

    # Process each directory and its file patterns
    for i, dir_name in enumerate(dirs):
        dir_path = os.path.join(base_path, dir_name)

        # Create directory if it doesn't exist
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"  ✓ Created {dir_name}/")

        # Move subdirectories if specified
        if dir_mappings and i < len(dir_mappings):
            for subdir_name in dir_mappings[i]:
                if subdir_name in subdirs and subdir_name not in moved_dirs:
                    src = os.path.join(base_path, subdir_name)
                    dst = os.path.join(dir_path, subdir_name)
                    shutil.move(src, dst)
                    print(f"    Moved {subdir_name}/ -> {dir_name}/")
                    moved_dirs.add(subdir_name)

        patterns = file_mappings[i] if i < len(file_mappings) else []

        for pattern in patterns:
            if pattern == '*':
                # Move all remaining files
                for f in files:
                    if f not in moved_files:
                        src = os.path.join(base_path, f)
                        dst = os.path.join(dir_path, f)
                        shutil.move(src, dst)
                        print(f"    Moved {f} -> {dir_name}/")
                        moved_files.add(f)
            else:
                # Move files matching this pattern
                for f in files:
                    if f not in moved_files and fnmatch.fnmatch(f, pattern):
                        src = os.path.join(base_path, f)
                        dst = os.path.join(dir_path, f)
                        shutil.move(src, dst)
                        print(f"    Moved {f} -> {dir_name}/")
                        moved_files.add(f)

    return True


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
