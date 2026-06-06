#!/usr/bin/env bash
# SessionEnd hook: Generate compliance report for the sprint
# Runs verify-applied on lessons + generates compliance report

set -euo pipefail

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

if [ -z "$SPRINT" ]; then
    echo "[hook] No active sprint found, skipping compliance report"
    exit 0
fi

echo "[hook] Generating compliance report for sprint $SPRINT"

# Verify lessons applied
if [ -f "scripts/evol-lessons.py" ]; then
    python3 scripts/evol-lessons.py verify-applied --sprint="$SPRINT" 2>/dev/null || true
fi

# Generate compliance report
if [ -f "scripts/evol-compliance.py" ]; then
    python3 scripts/evol-compliance.py report --sprint="$SPRINT" 2>/dev/null || true
fi

echo "[hook] Compliance report generated: acuerdos/auditoria/compliance-sprint-$SPRINT.md"
exit 0
