#!/usr/bin/env bash
# PostToolUse hook: Log PR URL after gh pr create

OUTPUT="$1"
if echo "$OUTPUT" | grep -q "github.com.*pull/"; then
    URL=$(echo "$OUTPUT" | grep -oE "https://github.com/[^ ]+/pull/[0-9]+" | head -1)
    echo "[HOOK] PR Created: $URL"
fi
exit 0