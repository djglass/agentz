from typer import Typer
from agentz import commands

app = Typer()
app.add_typer(commands.app, name="agentz")

if __name__ == "__main__":
    app()
