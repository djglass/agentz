# agentz/utils/rollup.py

from collections import Counter

def generate_risk_rollup(systems: list[dict]) -> str:
    """
    Generates a human-readable roll-up summary of risk levels across matched systems.

    Args:
        systems (list): List of matched system dictionaries.

    Returns:
        str: Formatted summary string.
    """
    risk_levels = Counter(s.get("risk_level", "Unknown") for s in systems)
    total = len(systems)

    lines = [f"Total matched systems: {total}"]
    for level in ["Critical", "High", "Medium", "Low", "Unknown"]:
        count = risk_levels.get(level, 0)
        if count > 0:
            lines.append(f" • {level}: {count}")

    return "\n".join(lines)

def summarize_high_risk_systems(systems: list[dict], limit: int = 5) -> str:
    """
    Returns a plain-text bullet list of high/critical systems with highest confidence scores.

    Args:
        systems (list): List of system dicts with risk_level and confidence_score fields.
        limit (int): Max number of entries to include.

    Returns:
        str: Structured summary.
    """
    filtered = [s for s in systems if s.get("risk_level") in {"High", "Critical"}]
    top = sorted(filtered, key=lambda s: int(s.get("confidence_score", 0)), reverse=True)[:limit]

    if not top:
        return "No high-risk systems identified."

    lines = []
    for s in top:
        line = f"{s.get('hostname', 'Unknown')} | Risk: {s.get('risk_level')} | Confidence: {s.get('confidence_score')} | Criticality: {s.get('Criticality')} | Environment: {s.get('Environment')}"
        lines.append(f" • {line}")

    return "\n".join(lines)
