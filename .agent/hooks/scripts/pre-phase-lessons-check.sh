#!/usr/bin/env bash
# PreToolUse hook: Check pending lessons before phase
# Shows relevant pending lessons so the agent can avoid repeating mistakes

set -euo pipefail

INPUT=$(cat)
PHASE=""

if echo "$INPUT" | grep -q '^{'; then
    PHASE=$(echo "$INPUT" | python3 -c "
import sys, json, re
d = json.load(sys.stdin)
cmd = d.get('command', '') or d.get('prompt', '') or ''
m = re.search(r'/evol\s+(briefing|doc-granular|historias|build|qa|retro|idea|discovery)', cmd)
if m:
    phases = {'idea':'0.5','discovery':'0.7','briefing':'1','doc-granular':'2','historias':'3','build':'4','qa':'5','retro':'6'}
    print(phases.get(m.group(1), ''))
" 2>/dev/null || echo "")
fi

if [ -n "$PHASE" ] && [ -f "scripts/evol-compliance.py" ]; then
    RESULT=$(python3 scripts/evol-compliance.py check-lessons --fase="$PHASE" 2>&1)

    if echo "$RESULT" | grep -q "Pendientes relevantes: [1-9]"; then
        echo "[evol-hook] LESSONS: Pending lessons apply to this phase:" >&2
        echo "$RESULT" | grep -E "^\s+-" >&2
        echo "[evol-hook] Review these lessons before proceeding." >&2
    fi
fi

exit 0
