# agentz/utils/confidence.py

def compute_confidence_score(cve_keywords: set, system: dict) -> int:
    """
    Computes a numeric confidence score (0–100) estimating the likelihood
    that the system is vulnerable based on software/OS keyword overlap.

    Args:
        cve_keywords (set): Keywords extracted from CVE metadata.
        system (dict): CMDB system record with normalized software and OS fields.

    Returns:
        int: Confidence score between 0 (low) and 100 (high).
    """
    fingerprint = (
        f"{system.get('hostname', '')} "
        f"{system.get('os', '')} "
        f"{system.get('Normalized OS', '')} "
        f"{system.get('Software', '')} "
        f"{system.get('Normalized Software', '')} "
        f"{' '.join(system.get('apps', []))}"
    ).lower()

    if not cve_keywords or not fingerprint:
        return 0

    matches = sum(1 for kw in cve_keywords if kw in fingerprint)
    score = min(int((matches / len(cve_keywords)) * 100), 100)
    return score

