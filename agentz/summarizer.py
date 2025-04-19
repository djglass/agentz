import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

KEV_FILE = Path("data/kev.json")
console = Console()

def summarize_threats():
    if not KEV_FILE.exists():
        console.print("[red]No KEV feed found. Run `agentz fetch` first.[/red]")
        return

    with open(KEV_FILE) as f:
        data = json.load(f)

    vulnerabilities = data.get("vulnerabilities", [])

    if not vulnerabilities:
        console.print("[yellow]No vulnerabilities found in KEV feed.[/yellow]")
        return

    table = Table(title="🚨 Top 5 KEV Vulnerabilities", show_lines=True)
    table.add_column("CVE ID", style="cyan", no_wrap=True)
    table.add_column("Vendor", style="magenta")
    table.add_column("Product", style="green")
    table.add_column("Due Date", style="red")
    table.add_column("Description", style="white")

    for vuln in vulnerabilities[:5]:
        table.add_row(
            vuln.get("cveID", "N/A"),
            vuln.get("vendorProject", "N/A"),
            vuln.get("product", "N/A"),
            vuln.get("dueDate", "N/A"),
            vuln.get("shortDescription", "N/A"),
        )

    console.print(table)
