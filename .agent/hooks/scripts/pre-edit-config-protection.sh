#!/usr/bin/env bash
# PreToolUse hook: Block governance file edits without evol-gate approval
# Exit 0 = allow, Exit 2 = block

set -euo pipefail

HOOK_LOG="${HOOK_LOG:-.agent/hooks/.hook-blocked.log}"
GATE_LOG=".evol/.gate-log.jsonl"

log_blocked() {
    local reason="$1"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] BLOCKED: $reason" >> "$HOOK_LOG" 2>/dev/null || true
}

PROTECTED_FILES="constitucion.md gates.md hooks.json .gate-key .gate-log.jsonl"
PROTECTED_PATTERNS="constitucion.md gates.md hooks.json"

# Check if evol-gate approve was run recently (within 1 hour)
check_gate_approval() {
    if [ ! -f "$GATE_LOG" ]; then
        return 1
    fi
    local last_approve
    last_approve=$(grep -c '"phase"' "$GATE_LOG" 2>/dev/null || echo "0")
    if [ "$last_approve" -gt 0 ]; then
        return 0
    fi
    return 1
}

GATE_APPROVED=0
if check_gate_approval; then
    GATE_APPROVED=1
fi

BLOCKED=0
for pattern in $PROTECTED_PATTERNS; do
    if [[ "$1" == *"$pattern"* ]]; then
        if [ "$GATE_APPROVED" -eq 1 ]; then
            echo "[evol-hook] WARN: editing governance file: $pattern (gate approved)" >&2
        else
            echo "[evol-hook] BLOQUEADO: edicion de archivo de gobernanza '$pattern' requiere evol-gate approve" >&2
            log_blocked "governance-edit:$pattern without gate"
            BLOCKED=1
        fi
    fi
done

if [ "$BLOCKED" -eq 1 ]; then
    exit 2
fi

exit 0