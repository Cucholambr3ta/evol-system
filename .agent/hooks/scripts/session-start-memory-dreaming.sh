#!/usr/bin/env bash
# SessionStart hook: Run dreaming engine to consolidate recent memories
# This helps maintain persistence by consolidating recent experiences

PROJECT="${EVOL_PROJECT:-.}"

if command -v python3 &>/dev/null && [ -f "scripts/evol-memory.py" ]; then
    echo "--- Memory Dreaming (v2) ---"
    
    # Run dreaming engine to consolidate recent memories
    python3 scripts/evol-memory.py edms-dreaming 2>/dev/null || echo "  [dreaming] Skipped or error"
    
    # Get recent conflicts to be aware of
    python3 scripts/evol-memory.py edms-conflicts 2>/dev/null || true
    
    echo "--- Dreaming Complete ---"
fi

exit 0
