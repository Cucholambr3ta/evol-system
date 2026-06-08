#!/usr/bin/env bash
# SessionEnd hook: Run v2 memory persistence engines
# - Reflection: Analyze patterns and trends
# - Dreaming: Consolidate recent memories
# - Forgetting: Clean up expired items

PROJECT="${EVOL_PROJECT:-.}"

if command -v python3 &>/dev/null && [ -f "scripts/evol-memory.py" ]; then
    echo "--- Memory Persistence (v2) ---"
    
    # Run reflection engine (analyze patterns)
    echo "  Running reflection engine..."
    python3 scripts/evol-memory.py edms-reflection 2>/dev/null || echo "    [reflection] Skipped or error"
    
    # Run dreaming engine (consolidate memories)
    echo "  Running dreaming engine..."
    python3 scripts/evol-memory.py edms-dreaming 2>/dev/null || echo "    [dreaming] Skipped or error"
    
    # Run forgetting engine (clean up expired)
    echo "  Running forgetting engine..."
    python3 scripts/evol-memory.py edms-forget --max=10 2>/dev/null || echo "    [forgetting] Skipped or error"
    
    # Detect conflicts
    echo "  Detecting conflicts..."
    python3 scripts/evol-memory.py edms-conflicts 2>/dev/null || echo "    [conflicts] Skipped or error"
    
    echo "--- Persistence Complete ---"
fi

exit 0
