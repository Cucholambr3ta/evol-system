#!/usr/bin/env bash
# PreToolUse hook: Block dangerous commands
# Exit 0 = allow, Exit 2 = block

INPUT=$(cat)
COMMAND="${INPUT}"

# Bloquear rm -rf sobre directorios de sistema (no /tmp ni rutas profundas)
if echo "$COMMAND" | grep -qE 'rm[[:space:]]+-rf[[:space:]]+(--[[:space:]]+)?/(etc|usr|bin|sbin|lib|boot|root|home|var|opt)[/[:space:]$]'; then
    echo "[evol-hook] BLOQUEADO: rm -rf sobre directorio de sistema" >&2
    exit 2
fi

# Bloquear push --force a main/master
if echo "$COMMAND" | grep -qE 'git[[:space:]]+(push[[:space:]]+.*--force|push[[:space:]]+.*-f)[[:space:]]+(origin[[:space:]]*)?(main|master)'; then
    echo "[evol-hook] BLOQUEADO: force push a main/master" >&2
    exit 2
fi

# Bloquear chmod 777
if echo "$COMMAND" | grep -qE 'chmod[[:space:]]+777'; then
    echo "[evol-hook] BLOQUEADO: chmod 777" >&2
    exit 2
fi

# Bloquear curl/wget pipe a sh
if echo "$COMMAND" | grep -qE '(curl|wget)[[:space:]].*[|][[:space:]]*(ba)?sh'; then
    echo "[evol-hook] BLOQUEADO: curl/wget pipe a shell" >&2
    exit 2
fi

exit 0