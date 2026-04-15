from __future__ import annotations

import sys

import typer

from clikunja.commands.api import api_cmd
from clikunja.commands.auth import auth_app, login
from clikunja.commands.comments import comments_app
from clikunja.commands.labels import labels_app
from clikunja.commands.projects import projects_app
from clikunja.commands.tasks import tasks_app
from clikunja.errors import CLIError

app = typer.Typer(
    name="clikunja",
    help="CLI for Vikunja TODO.",
    no_args_is_help=True,
    add_completion=False,
)

app.command("login", help="Log in with an API token.")(login)
app.add_typer(auth_app, name="auth")
app.command("api", help="Raw authenticated Vikunja API passthrough.")(api_cmd)
app.add_typer(projects_app, name="projects")
app.add_typer(tasks_app, name="tasks")
app.add_typer(labels_app, name="labels")
app.add_typer(comments_app, name="comments")


def _run() -> None:
    try:
        app(standalone_mode=False)
    except CLIError as e:
        typer.echo(str(e), err=True)
        sys.exit(getattr(e, "exit_code", 1))
    except typer.Exit as e:
        sys.exit(e.exit_code)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        typer.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    _run()
