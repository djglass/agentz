DEPARTMENT_RISK_WEIGHTS = {
    "finance": 1.3,
    "security": 1.2,
    "product": 1.1,
    "sales": 1.0,
    "marketing": 1.0,
    "hr": 0.9,
    "it": 0.8,
    "legal": 1.0,
}

def calculate_confidence(system: dict, cve_data: dict, context_doc: str) -> int:
    score = 0
    os = system.get("Normalized OS", "").lower()
    sw = system.get("Normalized Software", "").lower()
    hostname = system.get("hostname", "").lower()
    context = context_doc.lower()
    cve_text = f"{cve_data.get('shortDescription', '')} {cve_data.get('product', '')}".lower()

    # OS match
    if any(os_match in os for os_match in ["windows", "linux", "ubuntu", "rhel"]):
        if any(os_match in cve_text for os_match in os.split()):
            score += 20

    # Software match
    if any(sw_match in sw for sw_match in cve_text.split()):
        score += 20

    # Internet exposure
    if "cloud" in system.get("Environment", "").lower() or "endpoint" in system.get("Type", "").lower():
        score += 15
    elif "action allow" in context and hostname in context:
        score += 10

    # Patch / compliance mentions
    if "patched" in context or "compliant" in context:
        score -= 15
    if "outdated" in context or "unpatched" in context:
        score += 10

    return max(0, min(score, 100))


def calculate_inherent_risk(system: dict) -> str:
    score = 0

    # Base score
    if system.get("Criticality", "").lower() == "high":
        score += 40
    if system.get("Environment", "").lower() == "production":
        score += 30
    if system.get("Normalized OS", "").lower().startswith("windows"):
        score += 10
    if system.get("system_type", "").lower() in {"public web", "vpn gateway"}:
        score += 20

    # Department weighting
    dept = system.get("Department", "").lower()
    multiplier = DEPARTMENT_RISK_WEIGHTS.get(dept, 1.0)
    adjusted = int(score * multiplier)

    if adjusted >= 80:
        return "Critical"
    elif adjusted >= 60:
        return "High"
    elif adjusted >= 40:
        return "Moderate"
    else:
        return "Low"
