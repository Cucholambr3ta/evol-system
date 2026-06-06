#!/usr/bin/env bash
# SessionStart hook: Load memoria.md, WORKING-CONTEXT, and EDMS wake-up context

echo "=== Working Context ==="

if [ -f "memoria.md" ]; then
    echo "--- memoria.md ---"
    head -30 memoria.md
fi

if [ -f "WORKING-CONTEXT.md" ]; then
    echo "--- WORKING-CONTEXT.md ---"
    cat WORKING-CONTEXT.md
fi

# EDMS wake-up context (~170 tokens)
if command -v python3 &>/dev/null && [ -f "scripts/evol-memory.py" ]; then
    echo "--- EDMS wake-up ---"
    python3 scripts/evol-memory.py --project="." edms-wake-up 2>/dev/null || echo "[EDMS] No disponible"
fi

echo "==================="
exit 0