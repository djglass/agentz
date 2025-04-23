# agentz/utils/risk.py

def compute_risk_score(system: dict) -> tuple[str, int]:
    """
    Computes a risk level and numeric score (0–100) for a system based on:
    - Criticality
    - Environment exposure
    - Internet-facing flag
    - Confidence score
    - Department-based weighting
    """
    score = 0

    # Criticality
    criticality = system.get("Criticality", "").lower()
    if "critical" in criticality:
        score += 40
    elif "high" in criticality:
        score += 30
    elif "medium" in criticality:
        score += 20
    elif "low" in criticality:
        score += 10

    # Environment Exposure
    env = system.get("Environment", "").lower()
    if "cloud" in env or "prod" in env:
        score += 20
    elif "qa" in env or "test" in env:
        score += 10

    # Internet-facing
    if str(system.get("Internet Facing", "")).lower() == "true":
        score += 20

    # Confidence score (CVE matching)
    try:
        confidence = int(system.get("confidence_score", 0))
        score += min(confidence, 20)
    except Exception:
        pass

    # Department weighting
    dept = system.get("Department", "").lower()
    department_weights = {
        "security": 10,
        "finance": 10,
        "it": 5,
        "hr": 5,
        "marketing": 3
    }
    score += department_weights.get(dept, 0)

    # Bound
    score = min(score, 100)

    # Risk level
    if score >= 80:
        return "Critical", score
    elif score >= 60:
        return "High", score
    elif score >= 40:
        return "Medium", score
    else:
        return "Low", score
