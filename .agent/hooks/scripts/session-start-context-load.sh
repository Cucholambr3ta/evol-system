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

# Memory Stack L0+L1 (~600-900 tokens, replaces individual EDMS queries)
if command -v python3 &>/dev/null && [ -f "scripts/evol_memory_stack.py" ]; then
    echo "--- Memory Stack (L0+L1) ---"
    python3 scripts/evol_memory_stack.py --wake-up 2>/dev/null || echo "[MemoryStack] wake-up no disponible"
elif command -v python3 &>/dev/null && [ -f "scripts/evol-memory.py" ]; then
    # Fallback to individual EDMS queries if memory stack not available
    echo "--- EDMS wake-up ---"
    python3 scripts/evol-memory.py --project="." edms-wake-up 2>/dev/null || echo "[EDMS] wake-up no disponible"

    echo "--- EDMS blocked ---"
    python3 scripts/evol-memory.py --project="." edms-blocked 2>/dev/null || echo "[EDMS] blocked no disponible"

    echo "--- EDMS tensions ---"
    python3 scripts/evol-memory.py --project="." edms-tensions 2>/dev/null || echo "[EDMS] tensions no disponible"
fi

# Code Graph stats (~50 tokens)
if command -v python3 &>/dev/null && [ -f "scripts/evol_code_indexer.py" ]; then
    echo "--- Code Graph ---"
    python3 scripts/evol_code_indexer.py stats 2>/dev/null || echo "[CodeGraph] stats no disponible"
fi

# Emit session start event for real-time tracking
if command -v python3 &>/dev/null && [ -f "scripts/evol_traces.py" ]; then
    python3 -c "
from evol_traces import emit_session_start
emit_session_start(project='$(basename \"$(pwd)\")', agent='hook:session-start')
" 2>/dev/null || true
fi

echo "==================="
exit 0