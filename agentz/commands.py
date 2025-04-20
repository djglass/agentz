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

@app.command(name="query")
def query_cve(
    cve_id: str,
    summarize: bool = typer.Option(False, "--summarize", help="Use LLM to generate a summary and mitigation guidance.")
):
    """Get detailed information on a specific CVE."""
    from pathlib import Path
    import json
    from rich.console import Console
    from rich.panel import Panel
    from agentz.llm.loader import get_llm

    console = Console()
    data_file = Path("data/all_sources.json")

    if not data_file.exists():
        console.print("[red]No threat data found. Run `agentz fetch` first.[/red]")
        return

    with open(data_file) as f:
        items = json.load(f)

    match = next((v for v in items if v.get("cveID", "").lower() == cve_id.lower()), None)

    if not match:
        console.print(f"[yellow]No data found for CVE: {cve_id}[/yellow]")
        return

    fields = [
        f"[bold]CVE:[/bold] {match.get('cveID', 'N/A')}",
        f"[bold]Vendor:[/bold] {match.get('vendorProject', 'N/A')}",
        f"[bold]Product:[/bold] {match.get('product', 'N/A')}",
        f"[bold]Due Date:[/bold] {match.get('dueDate', 'N/A')}",
        f"[bold]Source:[/bold] {match.get('source', 'unknown')}",
        f"[bold]Description:[/bold]\n{match.get('shortDescription', 'N/A')}"
    ]

    console.print(Panel.fit("\n".join(fields), title=f"🔎 Details for {cve_id}"))

    if summarize:
        prompt = f"""You are a security analyst. Based on the following CVE details, generate:
1. A plain-language summary of the vulnerability.
2. Recommended remediations or mitigations for defenders.
3. Indicate that the source of this data is: {match.get('source', 'unknown')}.

Details:
CVE: {match.get('cveID', '')}
Vendor: {match.get('vendorProject', '')}
Product: {match.get('product', '')}
Due Date: {match.get('dueDate', '')}
Description: {match.get('shortDescription', '')}
"""

        console.print("[agentz] 🤖 Asking local LLM for analysis and guidance...\n")
        llm = get_llm()
        summary = llm.summarize(prompt)
        console.print(Panel.fit(summary, title="🧠 AI Summary & Guidance"))

@app.command(name="diff")
def diff(
    limit: int = typer.Option(10, help="Max number of new CVEs to display."),
    summarize: bool = typer.Option(False, help="Use LLM to summarize new CVEs.")
):
    """Show new CVEs since the last fetch, with optional summary."""
    from agentz.utils import tracker
    from agentz.llm.loader import get_llm
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    new_items = tracker.get_new_cves()

    if not new_items:
        console.print("[cyan]No new CVEs since last fetch.[/cyan]")
        return

    display_items = new_items[:limit]
    console.print(f"[green]🚨 {len(new_items)} new CVE(s) detected! Showing top {len(display_items)}:[/green]")

    for item in display_items:
        console.print(f" - [bold]{item['cveID']}[/bold] from {item.get('source', 'unknown')}: {item['shortDescription']}")

    if summarize:
        console.print("\n[agentz] 🤖 Summarizing new CVEs with local LLM...\n")
        prompt = "Summarize the following new CVEs and suggest possible mitigations:\n\n"
        for item in display_items:
            prompt += f"- {item['cveID']} ({item.get('source', 'unknown')}): {item['shortDescription']}\n"

        llm = get_llm()
        summary = llm.summarize(prompt)
        console.print(Panel.fit(summary.strip(), title="🧠 AI Summary"))

        # Log each summary line to file
        for item in display_items:
            tracker.log_summary(item["cveID"], summary)

from agentz.feeds.loader import load_feed

def pull_kev():
    print("🔄 Pulling CISA KEV feed...")
    load_feed("kev")
    print("✅ Done.")



