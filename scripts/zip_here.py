import zipfile
import os

# Start from wherever the script is located
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_zip = os.path.join(project_root, "agentz_project_trimmed.zip")

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", "logs", "agentz_state/rag_index", "agentz_state/rag_index_archive"}
EXCLUDE_FILES = {".DS_Store"}

def should_exclude(path):
    parts = set(path.split(os.sep))
    return parts & EXCLUDE_DIRS or os.path.basename(path) in EXCLUDE_FILES

with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(project_root):
        rel_root = os.path.relpath(root, project_root)
        if should_exclude(rel_root):
            continue
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, project_root)
            if not should_exclude(rel_path):
                zipf.write(filepath, rel_path)

print(f"✅ Project zipped to {output_zip}")

