class ThreatFeed:
    def fetch(self) -> list[dict]:
        """Return a list of threat items with a 'source' field."""
        raise NotImplementedError
