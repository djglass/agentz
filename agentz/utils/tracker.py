import json
from pathlib import Path
from datetime import datetime

KEV_PATH = Path("data/kev.json")
SEEN_FILE = Path("agentz_state/data/seen_cves.json")
LOG_FILE = Path("logs/summaries.log")

def get_seen_cves():
    if SEEN_FILE.exists():
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def load_kev_feed():
    if not KEV_PATH.exists():
        print(f"⚠️ KEV feed not found at {KEV_PATH}")
        return []
    with open(KEV_PATH) as f:
        data = json.load(f)
        # Handle nested structure
        if isinstance(data, dict) and "vulnerabilities" in data:
            return data["vulnerabilities"]
        return data  # fallback if already a flat list

def get_recent_cves(limit=5):
    seen_ids = get_seen_cves()
    cves = load_kev_feed()
    seen_cves = [cve for cve in cves if cve.get("cveID") in seen_ids]
    seen_cves = sorted(seen_cves, key=lambda x: x.get("dateAdded", ""), reverse=True)
    return seen_cves[:limit]

def lookup_cve(cve_id: str) -> dict:
    cves = load_kev_feed()
    return next((cve for cve in cves if cve.get("cveID") == cve_id), {})

def update_seen_cves(current_items):
    seen_ids = [item["cveID"] for item in current_items if "cveID" in item]
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(set(seen_ids)), f, indent=2)

def log_summary(cve_id, summary):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {cve_id}: {summary.strip()}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")
