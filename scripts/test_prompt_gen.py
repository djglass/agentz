import json
from agentz.rag.prompts import build_rag_prompt

# Load KEV feed and extract vulnerabilities list
with open("data/kev.json", "r") as f:
    kev_data = json.load(f)

vulns = kev_data.get("vulnerabilities", [])

# Use the first 3 for testing
test_cves = []
for entry in vulns[:3]:
    test_cves.append({
        "cveID": entry["cveID"],
        "vendorProject": entry.get("vendorProject", "UNKNOWN"),
        "product": entry.get("product", "UNKNOWN"),
        "shortDescription": entry.get("shortDescription", ""),
        "known_exploited": True,
        "internet_exposed": True if "web" in entry.get("product", "").lower() else False,
        "exposure_vector": "network"
    })

# Build and print the enriched prompt
prompt = build_rag_prompt(test_cves)
print(prompt)

