import os
import json
import requests
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path("agentz_state/cve_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
KEV_PATH = Path("data/kev.json")
KEV_LAST_FETCHED = Path("data/kev_last_updated.txt")

CIRCL_URL_TEMPLATE = "https://cve.circl.lu/api/cve/{}"


def _is_today(date_path):
    if not date_path.exists():
        return False
    try:
        with open(date_path) as f:
            last_date = f.read().strip()
        return last_date == datetime.utcnow().strftime("%Y-%m-%d")
    except:
        return False


def _update_kev():
    try:
        response = requests.get(KEV_URL, timeout=10)
        if response.status_code == 200:
            KEV_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(KEV_PATH, "w") as f:
                f.write(response.text)
            with open(KEV_LAST_FETCHED, "w") as f:
                f.write(datetime.utcnow().strftime("%Y-%m-%d"))
            return True
        else:
            print(f"⚠️ Failed to fetch KEV: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Exception while fetching KEV: {e}")
        return False


def _load_kev():
    if not KEV_PATH.exists():
        return []
    with open(KEV_PATH) as f:
        data = json.load(f)
        return data.get("vulnerabilities", [])


def _query_circl(cve_id):
    try:
        resp = requests.get(CIRCL_URL_TEMPLATE.format(cve_id), timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"⚠️ CIRCL returned status {resp.status_code} for {cve_id}")
            return None
    except Exception as e:
        print(f"⚠️ CIRCL error for {cve_id}: {e}")
        return None


def _load_cached_cve(cve_id):
    cache_file = CACHE_DIR / f"{cve_id}.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None


def _cache_cve(cve_id, data):
    cache_file = CACHE_DIR / f"{cve_id}.json"
    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)


def lookup_cve(cve_id):
    # Step 1: Try fresh KEV
    if not _is_today(KEV_LAST_FETCHED):
        _update_kev()
    kev = _load_kev()
    match = next((cve for cve in kev if cve.get("cveID") == cve_id), None)
    if match:
        _cache_cve(cve_id, match)
        return match

    # Step 2: CIRCL fallback
    print(f"🌐 CVE {cve_id} not found in KEV. Querying CIRCL...")
    circl = _query_circl(cve_id)
    if circl:
        cna = circl.get("containers", {}).get("cna", {})
        description = next((d.get("value") for d in cna.get("descriptions", []) if d.get("lang") == "en"), "No description available")
        vendor = cna.get("affected", [{}])[0].get("vendor", "Unknown")
        product = cna.get("affected", [{}])[0].get("product", "Unknown")
        result = {
            "cveID": cve_id,
            "shortDescription": description,
            "vendorProject": vendor,
            "product": product,
            "internet_exposed": False,
            "known_exploited": False,
            "qualitative_risk": "Medium",
            "exposure_vector": "unknown",
            "product_criticality": "low"
        }
        _cache_cve(cve_id, result)
        return result

    # Step 3: Cached fallback
    print(f"⚠️ CIRCL failed. Checking local cache...")
    cached = _load_cached_cve(cve_id)
    if cached:
        return cached

    # Step 4: Give up
    print(f"❌ CVE {cve_id} could not be found in KEV, CIRCL, or cache.")
    return None
