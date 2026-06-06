#!/usr/bin/env bash
# PostToolUse hook: Record phase metrics for compliance tracking
# Stores timing and artifact counts for sprint reports

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
    SPRINT=""
    if [ -f "acuerdos/sprints/INDEX.json" ]; then
        SPRINT=$(python3 -c "
import json
with open('acuerdos/sprints/INDEX.json') as f:
    data = json.load(f)
    for s in reversed(data.get('sprints', [])):
        if s.get('status') == 'active':
            print(s.get('number', ''))
            break
" 2>/dev/null || echo "")
    fi

    SPRINT_ARG=""
    [ -n "$SPRINT" ] && SPRINT_ARG="--sprint=$SPRINT"

    python3 scripts/evol-compliance.py record --fase="$PHASE" --agent="orchestrator" $SPRINT_ARG 2>/dev/null || true
fi

exit 0
