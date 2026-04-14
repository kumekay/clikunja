from __future__ import annotations

import json as _json
from typing import Any

import typer

from clikunja import config
from clikunja.client import Client
from clikunja.errors import APIError, AuthError


def die(msg: str, code: int = 1) -> None:
    typer.echo(msg, err=True)
    raise typer.Exit(code)


def get_client() -> Client:
    cfg = config.load()
    if not cfg.url or not cfg.token:
        die("Not logged in. Run `clikunja login` first.", 2)
    try:
        return Client(cfg.url, cfg.token)
    except AuthError as e:
        die(str(e), 2)


def call(method: str, path: str, **kw: Any) -> Any:
    client = get_client()
    try:
        return client.request(method, path, **kw)
    except AuthError as e:
        die(f"Authentication failed: {e}", 2)
    except APIError as e:
        die(f"API error: {e}", 3)


def print_json(data: Any) -> None:
    typer.echo(_json.dumps(data, indent=2))


def print_table(rows: list[dict], columns: list[tuple[str, str]]) -> None:
    """columns: list of (header, key) tuples."""
    if not rows:
        typer.echo("(no results)")
        return
    headers = [h for h, _ in columns]
    values: list[list[str]] = [
        [str(row.get(k, "") or "") for _, k in columns] for row in rows
    ]
    widths = [
        max(len(headers[i]), *(len(v[i]) for v in values)) for i in range(len(headers))
    ]
    sep = "  "
    typer.echo(sep.join(h.ljust(w) for h, w in zip(headers, widths, strict=False)))
    for row in values:
        typer.echo(
            sep.join(c.ljust(w) for c, w in zip(row, widths, strict=False))
        )
