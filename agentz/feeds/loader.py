from agentz.feeds.kev import KEVFeed
from agentz.feeds.abuse import AbuseFeed

FEED_MAP = {
    "kev": KEVFeed,
    "abuse": AbuseFeed
}

def load_feed(name):
    if name not in FEED_MAP:
        raise ValueError(f"Unsupported feed: {name}")
    return FEED_MAP[name]()
