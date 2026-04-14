from __future__ import annotations

import typer

from clikunja import config
from clikunja.client import Client
from clikunja.errors import APIError, AuthError


def _die(msg: str, code: int = 1) -> None:
    typer.echo(msg, err=True)
    raise typer.Exit(code)

auth_app = typer.Typer(
    name="auth",
    help="Authentication: login, logout, status.",
    no_args_is_help=True,
)


def _mask_token(token: str | None) -> str:
    if not token:
        return "(none)"
    if len(token) <= 8:
        return "*" * len(token)
    return f"{token[:4]}…{token[-4:]}"


def _verify(url: str, token: str) -> dict:
    try:
        return Client(url, token).get("/user")
    except AuthError as e:
        _die(f"Authentication failed: {e}", 2)
    except APIError as e:
        _die(f"API error while verifying token: {e}", 3)


def login(
    url: str | None = typer.Option(None, "--url", help="Vikunja base URL."),
    token: str | None = typer.Option(None, "--token", help="API token."),
    check: bool = typer.Option(
        False, "--check", help="Verify credentials but do not modify saved config."
    ),
) -> None:
    """Log in to a Vikunja instance with an API token."""
    existing = config.load()
    url = url or existing.url
    if not url:
        url = typer.prompt("Vikunja URL")
    if not token:
        token = typer.prompt("API token", hide_input=True)

    user = _verify(url, token)
    username = user.get("username") or user.get("name") or "user"
    if check:
        typer.echo(f"OK. Authenticated as {username} at {url} (config unchanged).")
        return

    config.save(config.Config(url=url, token=token))
    typer.echo(f"Logged in to {url} as {username}.")


@auth_app.command("status")
def status() -> None:
    """Show the current logged-in URL, masked token, and /user reachability."""
    cfg = config.load()
    if not cfg.url or not cfg.token:
        _die("Not logged in. Run `clikunja login` first.", 2)
    try:
        user = Client(cfg.url, cfg.token).get("/user")
    except AuthError as e:
        _die(f"Authentication failed: {e}", 2)
    except APIError as e:
        _die(f"API error: {e}", 3)

    username = user.get("username") or user.get("name") or "user"
    typer.echo(f"URL:   {cfg.url}")
    typer.echo(f"Token: {_mask_token(cfg.token)}")
    typer.echo(f"User:  {username}")


@auth_app.command("logout")
def logout() -> None:
    """Forget the stored API token (URL is retained)."""
    cfg = config.load()
    config.save(config.Config(url=cfg.url, token=None))
    typer.echo("Token removed.")
