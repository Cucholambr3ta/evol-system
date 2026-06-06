#!/usr/bin/env bash
# PreToolUse hook: Pre-phase compliance check
# Validates artifacts + gate + lessons BEFORE allowing phase progression
# Exit 0 = allow, Exit 2 = block

set -euo pipefail

INPUT=$(cat)
PHASE=""

# Try to extract phase from context (evol phase transition)
if echo "$INPUT" | grep -q '^{'; then
    PHASE=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
cmd = d.get('command', '') or d.get('prompt', '') or ''
# Detect phase transitions: /evol briefing, /evol build, etc.
import re
m = re.search(r'/evol\s+(briefing|doc-granular|historias|build|qa|retro|idea|discovery)', cmd)
if m:
    phases = {'idea':'0.5','discovery':'0.7','briefing':'1','doc-granular':'2','historias':'3','build':'4','qa':'5','retro':'6'}
    print(phases.get(m.group(1), ''))
" 2>/dev/null || echo "")
fi

# If we detected a phase, run compliance check
if [ -n "$PHASE" ] && [ -f "scripts/evol-compliance.py" ]; then
    SPRINT=""
    if [ -f "acuerdos/sprints/INDEX.json" ]; then
        SPRINT=$(python3 -c "
import json
with open('acuerdos/sprints/INDEX.json') as f:
    data = json.load(f)
    sprints = data.get('sprints', [])
    for s in reversed(sprints):
        if s.get('status') == 'active':
            print(s.get('number', ''))
            break
" 2>/dev/null || echo "")
    fi

    SPRINT_ARG=""
    [ -n "$SPRINT" ] && SPRINT_ARG="--sprint=$SPRINT"

    RESULT=$(python3 scripts/evol-compliance.py check --fase="$PHASE" $SPRINT_ARG 2>&1)
    RC=$?

    if [ "$RC" -eq 2 ]; then
        echo "[evol-hook] COMPLIANCE BLOCK: $RESULT" >&2
        exit 2
    fi

    if echo "$RESULT" | grep -q "WARN:"; then
        echo "[evol-hook] COMPLIANCE WARN: $RESULT" >&2
    fi
fi

exit 0
