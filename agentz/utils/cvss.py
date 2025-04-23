import os
import json
import requests

CACHE_PATH = "agentz_state/cvss_cache.json"
CIRCL_API_URL = "https://cve.circl.lu/api/cve/{}"
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_API_KEY = os.getenv("NVD_API_KEY")

def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

def get_cvss_score(cve_id, force_refresh=False):
    cache = load_cache()
    if not force_refresh and cve_id in cache:
        return cache[cve_id]

    result = try_circl(cve_id)

    # If CIRCL returns no usable CVSS data, fallback to NVD
    if not result["cvss_v3"] and not result["cvss_v2"]:
        fallback = try_nvd(cve_id)
        if fallback:
            result.update(fallback)

    # Cache the result (even partial)
    cache[cve_id] = result
    save_cache(cache)
    return result

def try_circl(cve_id):
    url = CIRCL_API_URL.format(cve_id)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "cvss_v2": data.get("cvss"),
            "cvss_v3": data.get("cvss3"),
            "cvss_v4": None
        }
    except requests.RequestException as e:
        print(f"⚠️ CIRCL API error for {cve_id}: {e}")
        return {"cvss_v2": None, "cvss_v3": None, "cvss_v4": None}

def try_nvd(cve_id):
    if not NVD_API_KEY:
        print("⚠️ NVD_API_KEY is not set. Skipping NVD fallback.")
        return None

    try:
        params = {
            "cveId": cve_id,
            "apiKey": NVD_API_KEY
        }
        response = requests.get(NVD_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        match = next((v for v in data.get("vulnerabilities", [])
                      if v.get("cve", {}).get("id") == cve_id), None)
        if not match:
            print(f"⚠️ No exact match for {cve_id} in NVD response")
            return None

        metrics = match.get("metrics", {})
        cvss_v3 = metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseScore")
        cvss_v2 = metrics.get("cvssMetricV2", [{}])[0].get("cvssData", {}).get("baseScore")
        cvss_v4 = metrics.get("cvssMetricV40", [{}])[0].get("cvssData", {}).get("baseScore")

        return {
            "cvss_v2": cvss_v2,
            "cvss_v3": cvss_v3,
            "cvss_v4": cvss_v4
        }

    except requests.RequestException as e:
        print(f"❌ NVD API error for {cve_id}: {e}")
        return None
