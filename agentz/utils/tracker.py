import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data/all_sources.json")
SEEN_FILE = Path("data/seen_cves.json")
LOG_FILE = Path("logs/summaries.log")

def get_seen_cves():
    if SEEN_FILE.exists():
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def get_current_cves():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE) as f:
        data = json.load(f)
    return data

def get_new_cves():
    seen = get_seen_cves()
    current = get_current_cves()
    new = [item for item in current if item.get("cveID") not in seen]
    return new

def update_seen_cves(current_items):
    seen_ids = [item["cveID"] for item in current_items]
    SEEN_FILE.parent.mkdir(exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(set(seen_ids)), f, indent=2)

def log_summary(cve_id, summary):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {cve_id}: {summary.strip()}"
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")
