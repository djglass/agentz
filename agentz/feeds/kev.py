import requests
from pathlib import Path
import json
from agentz.feeds.base import ThreatFeed

class KEVFeed(ThreatFeed):
    URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    OUTFILE = Path("data/kev.json")

    def fetch(self):
        print("[agentz] 📡 Fetching CISA KEV feed...")
        response = requests.get(self.URL, timeout=15)
        response.raise_for_status()
        self.OUTFILE.parent.mkdir(exist_ok=True)
        self.OUTFILE.write_text(response.text)
        data = json.loads(response.text)
        for item in data.get("vulnerabilities", []):
            item["source"] = "CISA KEV"
        return data.get("vulnerabilities", [])
