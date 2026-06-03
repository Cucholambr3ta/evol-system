#!/usr/bin/env bash
# Stop hook: Extract patterns for instincts

if command -v python3 >/dev/null 2>&1; then
    if [ -f "scripts/evol-state.py" ]; then
        python3 scripts/evol-state.py record-instinct \
            --pattern "session_pattern" \
            --context "auto-extracted" \
            --confidence 0.3 \
            --source "stop-hook" 2>/dev/null || true
    fi
fi
exit 0