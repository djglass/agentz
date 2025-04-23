import json
import os

PRODUCT_CRITICALITY_PATH = "data/product_criticality.json"

def load_product_criticality():
    if os.path.exists(PRODUCT_CRITICALITY_PATH):
        with open(PRODUCT_CRITICALITY_PATH, "r") as f:
            return json.load(f)
    return {}

def get_criticality(product: str, criticality_map: dict) -> str:
    product = product.lower()
    for keyword, level in criticality_map.items():
        if keyword in product:
            return level
    return "low"

def get_exposure_vector(cve: dict) -> str:
    if cve.get("internet_exposed"):
        return "network"
    if cve.get("exposure_vector") in {"network", "local"}:
        return cve["exposure_vector"]
    return "unknown"

def enrich_cves_with_risk(cves: list[dict]) -> list[dict]:
    criticality_map = load_product_criticality()
    enriched = []

    for cve in cves:
        score = 0
        exposure = get_exposure_vector(cve)

        if cve.get("known_exploited", False):
            score += 2
        if exposure == "network":
            score += 1

        crit = get_criticality(cve.get("product", ""), criticality_map)
        if crit == "high":
            score += 2
        elif crit == "medium":
            score += 1

        if score >= 4:
            risk = "High"
        elif score >= 2:
            risk = "Medium"
        else:
            risk = "Low"

        cve["qualitative_risk"] = risk
        cve["exposure_vector"] = exposure
        cve["product_criticality"] = crit
        enriched.append(cve)

    return enriched
