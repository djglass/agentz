import typer
from agentz.summarizer import summarize_threats
from agentz.feeds.cisa import fetch_cisa_kev

app = typer.Typer()

@app.command(name="summarize")
def summarize():
    """Pull threat feeds and summarize them using selected LLM."""
    summarize_threats()

@app.command(name="fetch")
def fetch():
    """Fetch the latest CISA Known Exploited Vulnerabilities feed."""
    fetch_cisa_kev()
