from agentz.feeds.base import ThreatFeed

class AbuseFeed(ThreatFeed):
    def fetch(self):
        print("[agentz] ⚠️ Abuse.ch integration is stubbed.")
        return [{"cveID": "ABUSE-STUB", "shortDescription": "Placeholder", "source": "Abuse.ch"}]
