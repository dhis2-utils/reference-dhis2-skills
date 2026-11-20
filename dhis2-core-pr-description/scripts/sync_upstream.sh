#!/usr/bin/env bash
# Refresh references/ from the PR description guide in dhis2/wow-backend.
#
# Usage: bash scripts/sync_upstream.sh [git-ref]     (default: master, then main)
# Needs: curl. Writes references/guide.md, references/templates/*.md and
# references/upstream.txt (source ref + date). Review the diff before committing:
# the repo rules (AGENTS.md) forbid real people's names, so the sed below
# replaces the one known name; check new examples for others.
set -euo pipefail
cd "$(dirname "$0")/.."
REPO=dhis2/wow-backend
TYPES=(chore ci docs feat fix perf refactor test)

fetch() { curl -fsSL "https://raw.githubusercontent.com/$REPO/$1/$2"; }

REF=${1:-}
if [ -z "$REF" ]; then
  for r in master main; do
    if fetch "$r" pr-templates/README.md >/dev/null 2>&1; then REF=$r; break; fi
  done
fi
[ -n "$REF" ] || { echo "pr-templates/README.md not found on master/main; pass a ref (e.g. docs/pr-templates)" >&2; exit 1; }

anonymise() { sed -e 's/review comment from Jan\./review comment from a reviewer./'; }

mkdir -p references/templates
fetch "$REF" pr-templates/README.md | anonymise > references/guide.md
for t in "${TYPES[@]}"; do fetch "$REF" "pr-templates/$t.md" | anonymise > "references/templates/$t.md"; done
fetch "$REF" guides/git_commit_messages.md > references/title-rules.md
printf 'source: https://github.com/%s/tree/%s/pr-templates\nsynced: %s\n' "$REPO" "$REF" "$(date -u +%F)" > references/upstream.txt
echo "synced from $REPO@$REF"; git --no-pager diff --stat -- references 2>/dev/null || true
