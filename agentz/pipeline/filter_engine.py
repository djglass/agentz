# agentz/pipeline/filter_engine.py

from agentz.utils.tracker import get_systems_by_cve

class CVEFilterEngine:
    def __init__(self, cmdb_data):
        self.cmdb_data = cmdb_data

    def filter_systems(self, cve_data: dict) -> list:
        """
        Identify systems that could be affected by the CVE.
        Uses fuzzy matching on vendor, product, and OS fields.
        """
        if not cve_data:
            print("❌ No CVE data to filter on.")
            return []

        matched = get_systems_by_cve(cve_data, self.cmdb_data)
        print(f"🔎 Filter phase: matched {len(matched)} system(s) for CVE {cve_data.get('cveID')}")
        return matched
