import os
import shutil
import zipfile
import glob
from pathlib import Path

def prepare_submissions_folder(root_folder, submissions_folder="submissions_unzip"):
    submissions_path = os.path.join(root_folder, submissions_folder)
    os.makedirs(submissions_path, exist_ok=True)

    zip_path = os.path.join(root_folder, "submissions.zip")
    if not os.path.exists(zip_path):
        downloads_zip = os.path.join(Path.home(), "Downloads", "submissions.zip")
        if os.path.exists(downloads_zip):
            shutil.copy(downloads_zip, root_folder)
            print(f"Copied submissions.zip from Downloads to {root_folder}")
        else:
            raise FileNotFoundError("submissions.zip not found")

    print("Extracting submissions.zip...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(submissions_path)
    print("Extraction complete.")
    return submissions_path


def unzip_submission(zip_file):
    fname = os.path.splitext(zip_file)[0]
    os.makedirs(fname, exist_ok=True)
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(fname)
    return fname


def flatten(folder_name: str, exclude_dirs: list[str] = None):
    """
    Flatten nested directory structure, moving source files to the top level.
    Ignores build artifacts and IDE directories.
    
    Args:
        folder_name: Path to folder to flatten
        exclude_dirs: List of directory names to preserve (don't flatten)
    """
    if exclude_dirs is None:
        exclude_dirs = []
    
    # Normalize exclude_dirs to lowercase for case-insensitive matching
    exclude_dirs_lower = [d.lower() for d in exclude_dirs]
    
    # Directories to completely ignore (build artifacts, IDE files, etc.)
    ignore_dirs = {
        '.vs', 'x64', 'debug', 'release', 'build', 'bin', 'obj',
        '__macosx', '.git', '.vscode', '.idea', 'cmake-build-debug',
        'cmake-build-release', '.gradle', 'out', 'target'
    }
    
    # File extensions we care about
    source_extensions = {'.cpp', '.h', '.hpp', '.c', '.cc', '.cxx', '.txt', '.md'}
    
    level = 1
    while True:
        print(f"Flattening level {level}...")
        found_items = False
        
        for root, dirs, files in os.walk(folder_name):
            # Skip if we're in an excluded directory
            current_dir = os.path.basename(root).lower()
            if current_dir in exclude_dirs_lower:
                print(f"  Skipping excluded directory: {os.path.basename(root)}/")
                continue
            
            # Skip if we're in an ignored directory
            if current_dir in ignore_dirs:
                continue
            
            # Skip the top-level folder itself
            if root == folder_name:
                continue
            
            # Check if parent is an excluded directory
            parent_dir = os.path.basename(os.path.dirname(root)).lower()
            if parent_dir in exclude_dirs_lower:
                continue
            
            # Move only source files
            for file in files:
                _, ext = os.path.splitext(file.lower())
                
                # Only move files with source extensions
                if ext not in source_extensions:
                    continue
                
                src = os.path.join(root, file)
                dst = os.path.join(folder_name, file)
                
                # Handle duplicates
                if os.path.exists(dst):
                    base, ext = os.path.splitext(file)
                    counter = 1
                    while os.path.exists(dst):
                        dst = os.path.join(folder_name, f"{base}_{counter}{ext}")
                        counter += 1
                
                shutil.move(src, dst)
                print(f"  Moved: {file}")
                found_items = True
            
            # Only move excluded directories to top level (preserve their structure)
            for dir_name in dirs:
                if dir_name.lower() in exclude_dirs_lower:
                    src = os.path.join(root, dir_name)
                    dst = os.path.join(folder_name, dir_name)
                    if src != dst and not os.path.exists(dst):
                        shutil.move(src, dst)
                        print(f"  Moved directory: {dir_name}/")
                        found_items = True
        
        # Remove empty directories (except excluded and ignored ones)
        for root, dirs, files in os.walk(folder_name, topdown=False):
            for dir_name in dirs:
                dir_lower = dir_name.lower()
                if dir_lower in exclude_dirs_lower or dir_lower in ignore_dirs:
                    continue
                    
                dir_path = os.path.join(root, dir_name)
                if dir_path != folder_name:
                    try:
                        if not os.listdir(dir_path):  # Empty directory
                            os.rmdir(dir_path)
                            print(f"  Removed directory: {dir_name}/")
                    except OSError:
                        pass
        
        if not found_items:
            break
        
        level += 1
    
    print("Flattening complete.\n")
