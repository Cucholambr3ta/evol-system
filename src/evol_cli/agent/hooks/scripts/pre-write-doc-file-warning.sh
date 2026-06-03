#!/usr/bin/env bash
# PreToolUse hook: Warn if doc file outside canonical paths

DEST="$1"
CANONICAL_DOCS="docs/ .claude/ .opencode/ AGENTS.md CLAUDE.md memoria.md"

if [[ "$DEST" =~ \.md$ ]]; then
    IN_CANONICAL=false
    for path in $CANONICAL_DOCS; do
        if [[ "$DEST" == "$path"* ]]; then
            IN_CANONICAL=true
            break
        fi
    done
    if [ "$IN_CANONICAL" = false ]; then
        echo "[HOOK] WARN: Writing .md outside canonical paths: $DEST"
    fi
fi
exit 0