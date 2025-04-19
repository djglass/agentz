import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from agentz.llm.loader import get_llm

DATA_FILE = Path("data/all_sources.json")
console = Console()

def summarize_threats(mode="table"):
    if not DATA_FILE.exists():
        console.print("[red]No threat feed found. Run `agentz fetch` first.[/red]")
        return

    with open(DATA_FILE) as f:
        items = json.load(f)

    if not items:
        console.print("[yellow]No threats found in data/all_sources.json[/yellow]")
        return

    items = items[:5]  # Limit to top 5 for now

    if mode == "table":
        table = Table(title="🚨 Top 5 Vulnerabilities (All Sources)", show_lines=True)
        table.add_column("CVE ID", style="cyan", no_wrap=True)
        table.add_column("Vendor", style="magenta")
        table.add_column("Product", style="green")
        table.add_column("Due Date", style="red")
        table.add_column("Source", style="blue")
        table.add_column("Description", style="white")

        for vuln in items:
            table.add_row(
                vuln.get("cveID", "N/A"),
                vuln.get("vendorProject", "N/A"),
                vuln.get("product", "N/A"),
                vuln.get("dueDate", "N/A"),
                vuln.get("source", "unknown"),
                vuln.get("shortDescription", "N/A"),
            )

        console.print(table)

    elif mode == "llm":
        text_block = ""
        for vuln in items:
            text_block += f"- {vuln['cveID']} ({vuln.get('source', 'unknown')}): {vuln['shortDescription']}\n"

        llm = get_llm()
        console.print("[agentz] 🤖 Summarizing top threats with local LLM...\n")
        summary = llm.summarize(text_block)
        console.print(summary)

    else:
        console.print(f"[red]Unsupported mode: {mode}[/red]")
