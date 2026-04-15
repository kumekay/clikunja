#!/usr/bin/env bash
# End-to-end smoke test against a real Vikunja instance.
# Reads credentials from CLIKUNJA_URL / CLIKUNJA_TOKEN (or VIKUNJA_HOST /
# VIKUNJA_TOKEN as fallbacks). Creates a throwaway project, task, comment,
# and label, exercises the common subcommands, and cleans up afterwards.

set -euo pipefail

: "${CLIKUNJA_URL:=${VIKUNJA_URL:-}}"
: "${CLIKUNJA_TOKEN:=${VIKUNJA_TOKEN:-}}"
export CLIKUNJA_URL CLIKUNJA_TOKEN

if ! clikunja auth status >/dev/null 2>&1; then
    echo "skip: no valid clikunja credentials (set CLIKUNJA_URL+CLIKUNJA_TOKEN, VIKUNJA_URL+VIKUNJA_TOKEN, or run \`clikunja login\`)" >&2
    exit 0
fi

PROJECT_PREFIX="proj-clikunja-e2e-"
LABEL_PREFIX="lbl-clikunja-e2e-"

sweep_leftovers() {
    # SIGKILL or prior failures can leave orphan resources behind. Delete any
    # project or label whose title starts with our e2e prefix before running
    # the fresh scenario, so the suite stays idempotent across re-runs.
    clikunja projects list --json 2>/dev/null |
        python3 -c "
import json, sys
try:
    data = json.load(sys.stdin) or []
except Exception:
    sys.exit(0)
for p in data:
    if str(p.get('title', '')).startswith('$PROJECT_PREFIX'):
        print(p['id'])
" |
        while read -r leftover_id; do
            echo "sweep: deleting leftover project #$leftover_id"
            clikunja projects delete "$leftover_id" >/dev/null 2>&1 || true
        done
    clikunja labels list --json 2>/dev/null |
        python3 -c "
import json, sys
try:
    data = json.load(sys.stdin) or []
except Exception:
    sys.exit(0)
for l in data:
    if str(l.get('title', '')).startswith('$LABEL_PREFIX'):
        print(l['id'])
" |
        while read -r leftover_id; do
            echo "sweep: deleting leftover label #$leftover_id"
            clikunja labels delete "$leftover_id" >/dev/null 2>&1 || true
        done
}

sweep_leftovers

SUFFIX="clikunja-e2e-$$-$(date +%s)"
PID=""
TID=""
CID=""
LID=""

cleanup() {
    set +e
    [ -n "$CID" ] && [ -n "$TID" ] && clikunja comments delete --task "$TID" "$CID" >/dev/null 2>&1
    [ -n "$TID" ] && clikunja tasks delete "$TID" >/dev/null 2>&1
    [ -n "$LID" ] && clikunja labels delete "$LID" >/dev/null 2>&1
    [ -n "$PID" ] && clikunja projects delete "$PID" >/dev/null 2>&1
}
trap cleanup EXIT

id_of() {
    # Extract the trailing numeric id from CLI output like "Created project #5 title".
    awk '{for(i=1;i<=NF;i++) if ($i ~ /^#[0-9]+$/) {gsub("#","",$i); print $i; exit}}'
}

echo "== auth =="
clikunja auth status

echo "== projects =="
clikunja projects list >/dev/null
PID=$(clikunja projects create --title "${PROJECT_PREFIX}${SUFFIX}" --description "e2e" | id_of)
[ -n "$PID" ] || { echo "failed to parse project id" >&2; exit 1; }
echo "project id=$PID"
clikunja projects view "$PID" >/dev/null

echo "== tasks =="
clikunja tasks list >/dev/null
clikunja tasks list --project "$PID" >/dev/null
TID=$(clikunja tasks create --project "$PID" --title "task-${SUFFIX}" --description "body" --priority 2 | id_of)
[ -n "$TID" ] || { echo "failed to parse task id" >&2; exit 1; }
echo "task id=$TID"
clikunja tasks view "$TID" >/dev/null
clikunja tasks done "$TID" >/dev/null
clikunja tasks undone "$TID" >/dev/null

echo "== comments =="
CID=$(clikunja comments add --task "$TID" "e2e comment" | id_of)
[ -n "$CID" ] || { echo "failed to parse comment id" >&2; exit 1; }
echo "comment id=$CID"
clikunja comments list --task "$TID" >/dev/null

echo "== labels =="
clikunja labels list >/dev/null
LID=$(clikunja labels create --title "${LABEL_PREFIX}${SUFFIX}" --color 00ff00 | id_of)
[ -n "$LID" ] || { echo "failed to parse label id" >&2; exit 1; }
echo "label id=$LID"

echo "== api passthrough =="
clikunja api GET projects >/dev/null

echo "== all green =="
