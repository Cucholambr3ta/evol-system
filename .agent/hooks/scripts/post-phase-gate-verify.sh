#!/usr/bin/env bash
# PostToolUse hook: Verify gate signed after phase completion
# Warns if a phase finished without gate approval

set -euo pipefail

INPUT=$(cat)
PHASE=""

if echo "$INPUT" | grep -q '^{'; then
    PHASE=$(echo "$INPUT" | python3 -c "
import sys, json, re
d = json.load(sys.stdin)
cmd = d.get('command', '') or d.get('prompt', '') or ''
# Detect phase approval: APROBADO, gate approve
if 'APROBADO' in cmd or 'gate approve' in cmd:
    m = re.search(r'fase\s+(\S+)|phase\s+(\S+)|briefing|doc-granular|historias|build|qa|retro', cmd, re.IGNORECASE)
    if m:
        phases = {'briefing':'1','doc-granular':'2','historias':'3','build':'4','qa':'5','retro':'6'}
        for g in m.groups():
            if g and g.lower() in phases:
                print(phases[g.lower()])
                break
" 2>/dev/null || echo "")
fi

if [ -n "$PHASE" ] && [ -f "scripts/evol-compliance.py" ]; then
    python3 scripts/evol-compliance.py record --fase="$PHASE" --agent="orchestrator" 2>/dev/null || true
fi

exit 0
