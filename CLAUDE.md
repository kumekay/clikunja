# clikunja — Agent Instructions

CLI for Vikunja. Python 3.11+, Typer + httpx. Installable via `uv tool install`.

## TDD is mandatory

Red/green/refactor. Always.

- Write a failing test first. Run it. See the red.
- Implement the minimum code that turns it green.
- Refactor only while green.
- **No production code change without a preceding failing test** in the same commit or the immediately preceding commit.

If a change seems too small for a test, either write the test anyway or the change is a refactor (must have green tests before and after).

## Dev setup

```bash
uv sync --all-extras
uv run pytest            # all green before any commit
uv run pytest -k name    # single test
uv run ruff check .
uv run ruff format .
```

## Layout

```
src/clikunja/
├── __main__.py        # python -m clikunja
├── cli.py             # typer root, global flags, subcommand wiring
├── config.py          # XDG load/save, env overrides
├── client.py          # httpx wrapper, Bearer auth, base URL normalization
├── errors.py          # CLIError, AuthError, APIError
└── commands/
    ├── auth.py        # login, logout, status
    ├── api.py         # raw authenticated passthrough
    ├── projects.py
    ├── tasks.py
    ├── labels.py
    └── comments.py

tests/
├── conftest.py        # XDG isolation, httpx_mock base URL, no-network guard
└── test_<module>.py
```

## Testing conventions

- Use `typer.testing.CliRunner` for all command tests.
- Use `pytest-httpx` (`httpx_mock` fixture) for HTTP. **No real network in tests.** The `conftest.py` guard must fail loudly if a test opens a real socket.
- Isolate config: `monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))` in any test that touches `config.load/save`.
- Isolate env: every test that reads `CLIKUNJA_*` env vars must `monkeypatch.delenv(..., raising=False)` first or set deterministic values.
- Prefer assertions on exit code + stdout/stderr over internal state.

## Config & auth

- **API token only.** Do not add username/password login, JWT refresh, or OAuth.
- Token header: `Authorization: Bearer <token>`.
- Config path: `platformdirs.user_config_dir("clikunja")` → `config.yml`.
- Precedence: CLI flags > env (`CLIKUNJA_URL`, `CLIKUNJA_TOKEN`) > config file.
- File mode `0600` on write. Never log the token.

## HTTP client

- `client.Client(url, token)` normalizes URL: strip trailing `/`, append `/api/v1` if missing.
- Always JSON. Raise `APIError` on non-2xx with status + body.
- Timeout: `CLIKUNJA_TIMEOUT` (default 30s).

## CLI conventions

- Global flags on root: `--url`, `--token`, `--json`, `--debug`.
- `--json` switches structured commands to raw JSON output (no table).
- Exit codes: 0 ok, 1 generic error, 2 auth error, 3 API error, 4 config error.
- Never print the token. Mask as `tk_xx…xx` in `auth status`.

## API passthrough

`clikunja api <METHOD> <path>` is a raw authenticated call against the Vikunja API:

- `-f key=value` — string field (JSON body)
- `-F key=@file` — file contents as field value (`@-` for stdin)
- `--raw` — no JSON parse, print response body verbatim

Path is joined under `/api/v1`. Leading `/` optional.

## Install for local testing

```bash
uv tool install --editable .
clikunja --help
```

## Out of scope

Username/password login, JWT refresh, OAuth, interactive TUI, Windows paths.
