from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import typer

from clikunja import config
from clikunja.client import Client
from clikunja.errors import APIError, AuthError

HTTP_METHODS = {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}


def _die(msg: str, code: int = 1) -> None:
    typer.echo(msg, err=True)
    raise typer.Exit(code)


def _parse_field(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        _die(f"Invalid field (expected key=value): {raw!r}", 1)
    k, v = raw.split("=", 1)
    return k, v


def _read_file_value(value: str) -> str:
    if value == "-":
        return sys.stdin.read()
    return Path(value).read_text()


def _read_json_body(value: str) -> Any:
    if value == "-":
        raw = sys.stdin.read()
    elif value.startswith("@"):
        raw = Path(value[1:]).read_text()
    else:
        _die(f"--body must be '-' or @path (got {value!r})", 1)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        _die(f"Invalid JSON body: {e}", 1)


def api_cmd(
    method_or_path: str = typer.Argument(
        ..., metavar="METHOD_OR_PATH", help="HTTP method (default GET) or path if no method given."
    ),
    path: str | None = typer.Argument(None, metavar="[PATH]"),
    f: list[str] = typer.Option(
        None,
        "-f",
        help="String field for JSON body (key=value). Repeatable.",
    ),
    F: list[str] = typer.Option(
        None,
        "-F",
        help="File-valued field for JSON body (key=@path or key=@- for stdin). Repeatable.",
    ),
    body_source: str | None = typer.Option(
        None,
        "--body",
        help="Raw JSON body from @path or - for stdin.",
    ),
    raw: bool = typer.Option(
        False, "--raw", help="Print response body verbatim instead of JSON-parsed."
    ),
) -> None:
    """Raw authenticated passthrough to the Vikunja API."""
    cfg = config.load()
    if not cfg.url or not cfg.token:
        _die("Not logged in. Run `clikunja login` first.", 2)

    if path is None:
        method, req_path = "GET", method_or_path
    elif method_or_path.upper() in HTTP_METHODS:
        method, req_path = method_or_path.upper(), path
    else:
        _die(f"Unknown HTTP method: {method_or_path!r}", 1)

    if body_source is not None and (f or F):
        _die("Cannot combine --body with -f/-F.", 1)

    payload: Any | None = None
    if body_source is not None:
        payload = _read_json_body(body_source)
    elif f or F:
        payload = {}
        for item in f or []:
            k, v = _parse_field(item)
            payload[k] = v
        for item in F or []:
            k, v = _parse_field(item)
            if not v.startswith("@"):
                _die(f"-F value must start with '@' (got {v!r})", 1)
            payload[k] = _read_file_value(v[1:])

    client = Client(cfg.url, cfg.token)
    kwargs: dict = {}
    if payload is not None and (
        body_source is not None or method in {"POST", "PUT", "PATCH", "DELETE"}
    ):
        kwargs["json"] = payload

    try:
        if raw:
            import httpx

            url = client._url(req_path)  # noqa: SLF001
            resp = httpx.request(
                method,
                url,
                headers=client._headers(),
                timeout=client.timeout,
                **kwargs,  # noqa: SLF001
            )
            if resp.status_code >= 400:
                _die(f"API error {resp.status_code}: {resp.text[:500]}", 3)
            typer.echo(resp.text)
            return
        result = client.request(method, req_path, **kwargs)
    except AuthError as e:
        _die(f"Authentication failed: {e}", 2)
    except APIError as e:
        _die(f"API error: {e}", 3)

    if result is None:
        return
    typer.echo(json.dumps(result, indent=2))
