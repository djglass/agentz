import os
import requests
from pathlib import Path

CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
KEV_FILE = DATA_DIR / "kev.json"

def fetch_cisa_kev():
    print("[agentz] 📡 Fetching CISA KEV feed...")
    response = requests.get(CISA_KEV_URL, timeout=10)
    response.raise_for_status()

    with open(KEV_FILE, "w") as f:
        f.write(response.text)

    print(f"[agentz] ✅ KEV feed saved to {KEV_FILE}")
