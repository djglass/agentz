#!/usr/bin/env python3

import sys
from agentz.utils.cvss import get_cvss_score

def main():
    if len(sys.argv) < 2:
        print("Usage: python cvss_fetcher.py CVE-YYYY-NNNN [--refresh]")
        sys.exit(1)

    cve_id = sys.argv[1].strip().upper()
    force = "--refresh" in sys.argv

    print(f"🔍 Fetching CVSS scores for {cve_id} (refresh={force})...")
    score = get_cvss_score(cve_id, force_refresh=force)

    if not any(score.values()):
        print(f"⚠️ No CVSS scores found for {cve_id}")
    else:
        print(f"✅ {cve_id} CVSS Scores:")
        for version, value in score.items():
            print(f"  {version}: {value}")

if __name__ == "__main__":
    main()
