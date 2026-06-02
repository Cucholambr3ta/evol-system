#!/usr/bin/env bash
# Stop hook: Warn if uncommitted changes

if [ -d ".git" ]; then
    UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l)
    if [ "$UNCOMMITTED" -gt 0 ]; then
        echo "[HOOK] WARN: $UNCOMMITTED uncommitted changes"
        echo "[HOOK] Run: git add . && git commit -m '...'"
    fi
fi
exit 0