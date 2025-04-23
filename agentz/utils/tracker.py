import os
import json
import requests
from pathlib import Path
from datetime import datetime

KEV_PATH = Path("data/kev.json")
SEEN_FILE = Path("agentz_state/data/seen_cves.json")
LOG_FILE = Path("logs/summaries.log")
CACHE_FILE = Path("agentz_state/data/cve_cache.json")

def get_seen_cves():
    if SEEN_FILE.exists():
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def load_kev_feed():
    if KEV_PATH.exists():
        with open(KEV_PATH) as f:
            data = json.load(f)
            return data.get("vulnerabilities", [])
    return []

def update_kev_feed():
    try:
        print("🔄 Fetching fresh KEV feed from CISA...")
        resp = requests.get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json", timeout=10)
        if resp.status_code == 200:
            with open(KEV_PATH, "w") as f:
                f.write(resp.text)
            print("✅ KEV feed updated.")
        else:
            print(f"⚠️ Failed to fetch KEV: {resp.status_code}")
    except Exception as e:
        print(f"❌ Exception fetching KEV: {e}")

def get_recent_cves(limit=5):
    seen_ids = get_seen_cves()
    cves = load_kev_feed()
    seen_cves = [cve for cve in cves if cve.get("cveID") in seen_ids]
    seen_cves = sorted(seen_cves, key=lambda x: x.get("dateAdded", ""), reverse=True)
    return seen_cves[:limit]

def get_new_cves(limit=5):
    update_kev_feed()
    seen_ids = get_seen_cves()
    cves = load_kev_feed()
    new_cves = [cve for cve in cves if cve.get("cveID") not in seen_ids]
    new_cves = sorted(new_cves, key=lambda x: x.get("dateAdded", ""), reverse=True)
    return new_cves[:limit]

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

def lookup_cve(cve_id: str) -> dict | None:
    # Step 1: Try CISA KEV
    update_kev_feed()
    kev = load_kev_feed()
    match = next((cve for cve in kev if cve.get("cveID") == cve_id), None)
    if match:
        print(f"✅ Found {cve_id} in CISA KEV")
        short_desc = match.get("shortDescription", "No description available.")
        vendor = match.get("vendorProject", "Unknown")
        product = match.get("product", "Unknown")
        inferred = infer_relevant_software(short_desc)

        result = {
            "cveID": cve_id,
            "shortDescription": short_desc,
            "vendor": vendor,
            "products": [product],
            "relevant_software": inferred,
            "known_exploited": True,
            "internet_exposed": False,
            "qualitative_risk": "High",
            "exposure_vector": "network",
            "product_criticality": "medium"
        }
        _write_cache(cve_id, result)
        return result

    # Step 2: Try CIRCL
    print(f"🌐 CVE {cve_id} not found in KEV. Querying CIRCL...")
    try:
        resp = requests.get(f"https://cve.circl.lu/api/cve/{cve_id}", timeout=10)
        if resp.status_code == 200:
            circl = resp.json()
            cna = circl.get("containers", {}).get("cna", {})
            descriptions = cna.get("descriptions", [])
            summary = next((d["value"] for d in descriptions if d.get("lang") == "en"), "No description available.")
            vendor = cna.get("affected", [{}])[0].get("vendor", "Unknown")
            product = cna.get("affected", [{}])[0].get("product", "Unknown")
            inferred = infer_relevant_software(summary)

            result = {
                "cveID": cve_id,
                "shortDescription": summary,
                "vendor": vendor,
                "products": [product],
                "relevant_software": inferred,
                "known_exploited": False,
                "internet_exposed": False,
                "qualitative_risk": "Medium",
                "exposure_vector": "unknown",
                "product_criticality": "low"
            }
            _write_cache(cve_id, result)
            return result
        else:
            print(f"⚠️ CIRCL returned {resp.status_code} for {cve_id}")
    except Exception as e:
        print(f"❌ CIRCL error for {cve_id}: {e}")

    # Step 3: Check cache
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        if cve_id in cache:
            print(f"🗂️ Using cached data for {cve_id}")
            return cache[cve_id]

    # Step 4: Fail
    print(f"❌ CVE {cve_id} not found in KEV, CIRCL, or cache. Skipping risk analysis.")
    return None

def _write_cache(cve_id: str, data: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            cache = json.load(f)
    else:
        cache = {}
    cache[cve_id] = data
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_systems_by_cve(cve_data: dict, cmdb_data: list) -> list:
    matched_systems = []
    if not cve_data or not cmdb_data:
        print("❌ No CVE or CMDB data available.")
        return []

    # Use LLM-inferred software list if available
    keyword_list = cve_data.get("relevant_software", [])

    if not keyword_list:
        print("⚠️ No relevant_software field found. Falling back to raw text parsing.")
        raw_text = " ".join([
            cve_data.get("shortDescription", ""),
            " ".join(cve_data.get("products", [])) if isinstance(cve_data.get("products"), list) else cve_data.get("products", ""),
            cve_data.get("vendor", "")
        ]).lower()
        keyword_list = re.findall(r'\b[a-zA-Z0-9\.-]+\b', raw_text)

    cve_keywords = set(kw.lower() for kw in keyword_list)
    print(f"🔍 Matching CVE keywords: {sorted(cve_keywords)}")

    # Preview first 5 system fingerprints
    for i, system in enumerate(cmdb_data[:5]):
        fingerprint = (
            f"{system.get('hostname', '')} "
            f"{system.get('os', '')} "
            f"{system.get('Normalized OS', '')} "
            f"{system.get('Software', '')} "
            f"{system.get('Normalized Software', '')} "
            f"{' '.join(system.get('apps', []))}"
        ).lower()
        print(f"🧬 System #{i+1} fingerprint:   {fingerprint}")

    for system in cmdb_data:
        fingerprint = (
            f"{system.get('hostname', '')} "
            f"{system.get('os', '')} "
            f"{system.get('Normalized OS', '')} "
            f"{system.get('Software', '')} "
            f"{system.get('Normalized Software', '')} "
            f"{' '.join(system.get('apps', []))}"
        ).lower()

        if any(kw in fingerprint for kw in cve_keywords):
            matched_systems.append({
                **system,
                "system_id": system.get("Asset Tag")
            })

    print(f"✅ Matched {len(matched_systems)} system(s) to CVE {cve_data.get('cveID')}")
    return matched_systems


import pandas as pd

def get_cmdb_data():
    path = "agentz/data/systems.csv"
    if not os.path.exists(path):
        raise FileNotFoundError("CMDB not found at agentz/data/systems.csv")
    return pd.read_csv(path).to_dict(orient="records")

from agentz.llm.localstack_ollama import LocalstackOllamaLLM

def infer_relevant_software(cve_text: str) -> list[str]:
    """
    Uses the local LLM directly (no vectorstore) to infer relevant software and platforms.
    """
    prompt = (
        "You are a cybersecurity analyst. Based on the following CVE description, "
        "list the likely affected operating systems, software platforms, and application frameworks. "
        "Return a simple comma-separated list of keywords. Do not include version numbers.\n\n"
        f"CVE Description:\n{cve_text.strip()}\n\n"
        "Affected technologies:"
    )

    llm = LocalstackOllamaLLM()
    response = llm.invoke(prompt)
    keywords = response.strip().lower().replace("\n", "").replace(".", "")
    return [s.strip() for s in keywords.split(",") if s.strip()]

