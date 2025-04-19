import typer
from agentz.summarizer import summarize_threats

app = typer.Typer()

@app.command(name="summarize")
def summarize():
    """Pull threat feeds and summarize them using selected LLM."""
    summarize_threats()
