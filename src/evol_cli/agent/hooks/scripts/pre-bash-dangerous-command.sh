#!/usr/bin/env bash
# PreToolUse hook: Block dangerous commands
# Exit 0 = allow, Exit 2 = block

set -euo pipefail

INPUT=$(cat)
COMMAND="$INPUT"

# Try parse JSON if available (Claude Code passes structured input)
if echo "$INPUT" | grep -q '^{'; then
    COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command','') or d.get('prompt','') or '')" 2>/dev/null || echo "$INPUT")
fi

# Logging without secrets
log_blocked() {
    local reason="$1"
    local hook_log="${HOOK_LOG:-.agent/hooks/.hook-blocked.log}"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] BLOCKED: $reason" >> "$hook_log" 2>/dev/null || true
}

BLOCKED=0

# Block: rm -rf on root
if echo "$COMMAND" | grep -qE 'rm[[:space:]]+-rf[[:space:]]+/?$'; then
    echo "[evol-hook] BLOQUEADO: rm -rf /" >&2
    log_blocked "rm -rf /"
    BLOCKED=1
fi

# Block: rm -rf on home directory
if echo "$COMMAND" | grep -qE 'rm[[:space:]]+-rf[[:space:]]+~'; then
    echo "[evol-hook] BLOQUEADO: rm -rf ~" >&2
    log_blocked "rm -rf ~"
    BLOCKED=1
fi

# Block: rm -rf on protected system directories
if echo "$COMMAND" | grep -qE 'rm[[:space:]]+-rf[[:space:]]+(--[[:space:]]+)?/(etc|usr|bin|sbin|lib|boot|root|var|opt|dev|sys)'; then
    echo "[evol-hook] BLOQUEADO: rm -rf sobre directorio de sistema" >&2
    log_blocked "rm -rf /etc|/usr|/bin|..."
    BLOCKED=1
fi

# Block: dd if= (disk dump)
if echo "$COMMAND" | grep -qE 'dd[[:space:]]+if='; then
    echo "[evol-hook] BLOQUEADO: dd if= (operacion de disco cruda)" >&2
    log_blocked "dd if="
    BLOCKED=1
fi

# Block: mkfs (filesystem creation)
if echo "$COMMAND" | grep -qE 'mkfs'; then
    echo "[evol-hook] BLOQUEADO: mkfs (creacion de filesystem)" >&2
    log_blocked "mkfs"
    BLOCKED=1
fi

# Block: chmod -R 777
if echo "$COMMAND" | grep -qE 'chmod[[:space:]]+(-R[[:space:]]+|-R )?777'; then
    echo "[evol-hook] BLOQUEADO: chmod 777 o chmod -R 777" >&2
    log_blocked "chmod 777"
    BLOCKED=1
fi

# Block: curl | sh / wget | sh
if echo "$COMMAND" | grep -qE '(curl|wget)[[:space:]].*[|][[:space:]]*(ba)?sh'; then
    echo "[evol-hook] BLOQUEADO: curl/wget pipe a shell" >&2
    log_blocked "curl|wget | sh"
    BLOCKED=1
fi

# Block: bash <(curl ...)
if echo "$COMMAND" | grep -qE 'bash[[:space:]]*<[[:space:]]*\((curl|wget)'; then
    echo "[evol-hook] BLOQUEADO: process substitution con curl/wget" >&2
    log_blocked "bash <(curl...)"
    BLOCKED=1
fi

# Block: sudo without authorized context
if echo "$COMMAND" | grep -qE '^sudo[[:space:]]' && [ -z "${EVOL_SUDO_AUTHORIZED:-}" ]; then
    echo "[evol-hook] BLOQUEADO: sudo sin autorizacion explicita (EVOL_SUDO_AUTHORIZED no esta definido)" >&2
    log_blocked "sudo without EVOL_SUDO_AUTHORIZED"
    BLOCKED=1
fi

# Block: git push --force / --force-with-lease to protected branches
PROTECTED_BRANCHES="main|master|develop"
if echo "$COMMAND" | grep -qE "git[[:space:]]+push[[:space:]].*(--force-with-lease|--force-with-lease=.*)[[:space:]].*($PROTECTED_BRANCHES)"; then
    echo "[evol-hook] BLOQUEADO: git push --force-with-lease a rama protegida" >&2
    log_blocked "git push --force-with-lease"
    BLOCKED=1
fi

if echo "$COMMAND" | grep -qE "git[[:space:]]+push[[:space:]].*(-f|--force)[[:space:]].*($PROTECTED_BRANCHES)"; then
    echo "[evol-hook] BLOQUEADO: git push --force a rama protegida" >&2
    log_blocked "git push --force"
    BLOCKED=1
fi

if [ "$BLOCKED" -eq 1 ]; then
    exit 2
fi

exit 0