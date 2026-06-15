#!/usr/bin/env bash
# PostToolUse hook for ElevatorLang.
#
# After an Edit/Write/MultiEdit, this formats the touched Python file with
# ruff, applies safe lint fixes, and type-checks it with ty. Type errors are
# reported back to the agent (exit code 2) so they get fixed immediately.
#
# Input: the tool-call JSON is delivered on stdin; we read tool_input.file_path.
set -euo pipefail

payload="$(cat)"
file="$(printf '%s' "$payload" \
  | python3 -c 'import json, sys; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))' \
  2>/dev/null || true)"

# Only act on existing Python files.
[ -z "$file" ] && exit 0
case "$file" in
  *.py) ;;
  *) exit 0 ;;
esac
[ -f "$file" ] || exit 0

cd "${CLAUDE_PROJECT_DIR:-.}"

# Format and apply safe fixes (non-fatal: never block on formatting).
uv run ruff format "$file" >/dev/null 2>&1 || true
uv run ruff check --fix "$file" >/dev/null 2>&1 || true

# Type-check: surface failures to the agent.
if ! ty_output="$(uv run ty check "$file" 2>&1)"; then
  printf 'ty reporto errores de tipo en %s:\n%s\n' "$file" "$ty_output" >&2
  exit 2
fi

exit 0
