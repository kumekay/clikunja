---
name: using-clikunja
description: Use `clikunja` CLI for all interactions with Vikunja TODO instances — projects, tasks, labels, comments, and raw API access. Use when the user mentions Vikunja, shares a Vikunja URL, or asks to list/create/update tasks, projects, labels, or comments on a Vikunja host. Prefer `clikunja` over browser automation or generic HTTP fetching for any Vikunja data.
---

# Using `clikunja` For Vikunja

## Rule

When interacting with a Vikunja TODO instance, use the `clikunja` CLI. This covers projects, tasks, labels, comments, and any other Vikunja entities.

A single Vikunja instance is identified by its base URL (e.g. `https://todo.example.com`). The API lives under `/api/v1` — `clikunja` appends this automatically.

- Do not use `curl`, browser automation, or generic web fetching against a Vikunja host when `clikunja` can provide the data.
- Do not guess API paths when `clikunja --help` or `clikunja <group> --help` can answer directly.
- For endpoints without a dedicated subcommand, use `clikunja api`.

## Quick Reference

```bash
# Auth
clikunja login --url https://todo.example.com   # prompts for API token
clikunja auth status                              # verify / show current login
clikunja auth logout                              # forget token, keep URL

# Projects
clikunja projects list
clikunja projects view 3
clikunja projects create --title "..." --description "..."
clikunja projects edit 3 --title "..."
clikunja projects delete 3

# Tasks
clikunja tasks list                       # all tasks across projects
clikunja tasks list --project 3           # only tasks in project 3
clikunja tasks view 42
clikunja tasks create --project 3 --title "..." --description "..." --priority 3
clikunja tasks edit 42 --title "..."
clikunja tasks done 42                    # mark complete
clikunja tasks undone 42                  # reopen
clikunja tasks delete 42

# Labels
clikunja labels list
clikunja labels create --title "bug" --color ff0000
clikunja labels delete 5

# Comments (require --task)
clikunja comments list --task 42
clikunja comments add --task 42 "Looks good"
clikunja comments edit 9 --task 42 --body "..."
clikunja comments delete 9 --task 42

# Raw API access
clikunja api GET projects
clikunja api GET /projects/3
clikunja api PUT projects/3/tasks -f title="New" -f description="..."
clikunja api POST tasks/42 -f done=true          # note: -f sends strings; use --json when types matter
clikunja api DELETE projects/3
```

Every structured `list`/`view` command supports `--json` to emit raw JSON for scripting.

## Long-form bodies (descriptions, comments)

For multi-paragraph markdown bodies, write the content to a temp file first and pass it via `--description "$(cat /tmp/body.md)"` or, for the `api` passthrough, via `-F key=@/tmp/body.md` which reads the file verbatim:

```bash
# Task with long markdown description
clikunja tasks create --project 3 --title "Write docs" \
  --description "$(cat /tmp/task-body.md)"

# Comment with long body (positional)
clikunja comments add --task 42 "$(cat /tmp/comment.md)"

# Editing via api passthrough when a dedicated subcommand lacks the flag
clikunja api POST tasks/42 -F description=@/tmp/new-body.md
```

`-f key=value` sends a string field in the JSON body. `-F key=@path` reads the file's contents as the field value (`@-` reads stdin).

## URL Handling

If the user gives a Vikunja URL, parse the resource from the path and use the appropriate `clikunja` command.

Examples (replace `<host>` with the actual Vikunja hostname):

- Task URL: `https://<host>/tasks/42`
  → `clikunja tasks view 42`
- Project URL: `https://<host>/projects/3`
  → `clikunja projects view 3`
- Project list view: `https://<host>/projects/3/1`
  → project 3; `clikunja tasks list --project 3`

## Config & Environment

Config file: `$XDG_CONFIG_HOME/clikunja/config.yml` (mode `0600`).

Environment overrides (highest precedence after CLI flags):

- `CLIKUNJA_URL` — base URL, e.g. `https://todo.example.com`
- `CLIKUNJA_TOKEN` — API token (generate one in Vikunja web UI under Settings → API Tokens)
- `CLIKUNJA_TIMEOUT` — HTTP timeout in seconds (default `30`)

If both are set via env, no `clikunja login` is required — scripts and CI can run commands directly.

## Workflow

1. If the user references a Vikunja instance (URL, "my TODO", "Vikunja"), use `clikunja`.
2. If a dedicated subcommand exists, prefer it.
3. If not, use `clikunja api <METHOD> <path>` for direct API access.
4. If access fails, report the error clearly instead of switching tools.

## Failure Handling

- If `clikunja` is not authenticated, exit code 2 and message "Not logged in." — suggest `clikunja login`.
- If the API returns 401, exit code 2. Token is likely expired or revoked — suggest regenerating it in the web UI.
- If the API returns 404, verify the resource ID.
- If the API returns 403, report a permissions problem rather than falling back to another tool.
- Non-2xx responses surface as `API error <status>: <body>` on stderr with exit code 3.

## Common Mistakes

- Do not include `/api/v1` in `--url` when logging in — `clikunja` appends it. Both forms work, but prefer the bare host URL (`https://todo.example.com`).
- Do not pass the token as a positional arg or in shell history if avoidable — use `clikunja login` and paste at the prompt, or export `CLIKUNJA_TOKEN` in a shell-local scope.
- `comments list` and `comments add` require `--task <id>`; comments are always scoped to a task.
- `tasks done`/`undone` use `POST /tasks/{id}` with `{"done": true/false}` — do not attempt to `PUT` a full task object just to toggle completion.
- For `api` passthrough, `-f` sends all values as strings. If the server needs a non-string (e.g. boolean, number), prefer a dedicated subcommand or wrap with `clikunja api ... --raw` plus a hand-crafted request only as a last resort.
- Do not reach for `curl` or browser automation — `clikunja api` covers every Vikunja endpoint with auth already handled.
