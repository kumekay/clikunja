# clikunja

A CLI for [Vikunja](https://vikunja.io) inspired by `gh`. Configurable server URL, API-token auth, structured subcommands for projects/tasks/labels/comments, plus a `gh api`-style raw passthrough.

## Install

```bash
uv tool install git+https://github.com/kumekay/clikunja.git
```

Or editable from a local checkout:

```bash
uv tool install --editable .
```

## Configure

```bash
clikunja login --url https://your-vikunja.example.com
# paste API token (generate one in the Vikunja web UI: Settings → API Tokens)
```

Config is stored at `$XDG_CONFIG_HOME/clikunja/config.yml` (mode `0600`).

Environment overrides:

- `CLIKUNJA_URL` — server base URL (e.g. `https://todo.example.com`)
- `CLIKUNJA_TOKEN` — API token
- `CLIKUNJA_TIMEOUT` — HTTP timeout in seconds (default `30`)

## Usage

```bash
clikunja auth status
clikunja projects list
clikunja tasks list --project 3
clikunja tasks create --project 3 --title "Write docs"
clikunja tasks done 42
clikunja labels list
clikunja comments add --task 42 "Looks good"

# Raw API passthrough
clikunja api GET projects
clikunja api PUT projects/3/tasks -f title="From CLI"
```

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check .
```

See [CLAUDE.md](CLAUDE.md) for the TDD workflow and layout.

## License

MIT
