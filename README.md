# clikunja

A CLI for [Vikunja](https://vikunja.io). Configurable server URL, API-token auth, structured subcommands for projects/tasks/labels/comments, plus a raw API passthrough.

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
# paste API token at the prompt (generate one in the Vikunja web UI: Settings → API Tokens)

# If your terminal blocks paste at hidden prompts, pipe the token via stdin:
pbpaste | clikunja login --url https://your-vikunja.example.com --token-stdin
# or: clikunja login --url ... --token-stdin <<< "$YOUR_TOKEN"
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

## Agent skill

This repo ships a `using-clikunja` skill at [`using-clikunja/SKILL.md`](using-clikunja/SKILL.md). Install it into an agent that consumes skills (e.g. via the [`skills`](https://github.com/vercel-labs/skills) CLI):

```bash
npx skills add git@github.com:kumekay/clikunja.git --skill using-clikunja
```

Once installed, the agent will prefer `clikunja` over `curl` / browser automation whenever a Vikunja URL or task is mentioned.

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check .
```

See [CLAUDE.md](CLAUDE.md) for the TDD workflow and layout.

## License

MIT
