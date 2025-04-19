import typer
from agentz.summarizer import summarize_threats
from agentz.feeds import loader

app = typer.Typer()

@app.command(name="summarize")
def summarize(mode: str = typer.Option("table", help="Output mode: 'table' or 'llm'")):
    summarize_threats(mode=mode)

@app.command(name="fetch")
def fetch(source: str = typer.Option("kev", help="Feed to pull: kev, abuse, or all")):
    """Fetch threat intelligence data from one or more feeds."""
    sources = loader.FEED_MAP.keys() if source == "all" else [source]

    all_items = []
    for src in sources:
        feed = loader.load_feed(src)
        items = feed.fetch()
        all_items.extend(items)

    # Save to a unified file
    import json
    from pathlib import Path

    Path("data").mkdir(exist_ok=True)
    Path("data/all_sources.json").write_text(json.dumps(all_items, indent=2))
    print(f"[agentz] ✅ {len(all_items)} items saved to data/all_sources.json")
