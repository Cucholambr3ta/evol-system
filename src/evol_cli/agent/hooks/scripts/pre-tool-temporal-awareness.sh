#!/usr/bin/env bash
# PreToolUse hook: Inject sprint context

SPRINT_FILE=".sprint-active"
if [ -f "$SPRINT_FILE" ]; then
    echo "[HOOK] Active Sprint: $(cat "$SPRINT_FILE")"
fi
exit 0