#!/usr/bin/env bash
# SessionStart hook: Load memoria.md and WORKING-CONTEXT

echo "=== Working Context ==="

if [ -f "memoria.md" ]; then
    echo "--- memoria.md ---"
    head -30 memoria.md
fi

if [ -f "WORKING-CONTEXT.md" ]; then
    echo "--- WORKING-CONTEXT.md ---"
    cat WORKING-CONTEXT.md
fi

echo "==================="
exit 0