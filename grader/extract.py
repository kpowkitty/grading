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

def flatten_inner_folder(fname):
    cpp_files = glob.glob(os.path.join(fname, '*.cpp'))
    if cpp_files:
        return
    inner_folder = next((d for d in os.listdir(fname) if os.path.isdir(os.path.join(fname, d))), None)
    if inner_folder:
        inner_folder_path = os.path.join(fname, inner_folder)
        for item in os.listdir(inner_folder_path):
            shutil.move(os.path.join(inner_folder_path, item), fname)
