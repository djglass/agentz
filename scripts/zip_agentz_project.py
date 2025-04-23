import zipfile
import os

project_root = "agentz_prj"
output_zip = "agentz_project_trimmed.zip"

EXCLUDE_DIRS = {"__pycache__", ".venv", ".git", "logs", "agentz_state/rag_index", "agentz_state/rag_index_archive"}
EXCLUDE_FILES = {".DS_Store"}

def should_exclude(path):
    parts = set(path.split(os.sep))
    return parts & EXCLUDE_DIRS or os.path.basename(path) in EXCLUDE_FILES

with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(project_root):
        rel_root = os.path.relpath(root, project_root)
        if should_exclude(rel_root):
            continue
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, project_root)
            if not should_exclude(rel_path):
                zipf.write(filepath, rel_path)

print(f"✅ Project zipped to {output_zip}")
