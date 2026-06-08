#!/usr/bin/env bash
# PostToolUse hook: Capture tool failures as lesson candidates
# Triggered when a bash command fails (non-zero exit)

PROJECT="${EVOL_PROJECT:-.}"
EXIT_CODE="${CLAUDE_EXIT_CODE:-$1}"
COMMAND="${CLAUDE_COMMAND:-$2}"

# Only capture failures (exit code != 0)
if [ -n "$EXIT_CODE" ] && [ "$EXIT_CODE" != "0" ]; then
    # Create lesson candidate file
    LESSON_DIR="acuerdos/lecciones"
    mkdir -p "$LESSON_DIR"

    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    LESSON_FILE="$LESSON_DIR/failure-${TIMESTAMP}.md"

    cat > "$LESSON_FILE" << EOF
# Failure Captured — ${TIMESTAMP}

## Contexto
- Comando: \`${COMMAND:-unknown}\`
- Exit code: ${EXIT_CODE}
- Fecha: $(date -Iseconds)

## Problema
[Capturado automaticamente por hook post-tool:failure-capture]

## Leccion candidata
[Categorizar: ARQUITECTURA | SEGURIDAD | DOMINIO | TESTING | DEVOPS | PROCESO | HERRAMIENTAS]

## Fix sugerido
[Pendiente de revision humana]
EOF

    # Index into EDMS if available
    if command -v python3 &>/dev/null; then
        TEXT=$(cat "$LESSON_FILE")
        
        # v1: Index lesson
        python3 scripts/evol-memory.py --project="$PROJECT" edms-index \
            "Failure: exit code $EXIT_CODE, command: ${COMMAND:-unknown}" \
            --tipo=leccion \
            --agent="hook:failure-capture" 2>/dev/null

        # v2: Verbatim storage + entity extraction + auto-linking
        python3 scripts/evol-memory.py edms-store "$TEXT" --tipo=leccion 2>/dev/null
        python3 scripts/evol-memory.py edms-extract "$TEXT" 2>/dev/null
        python3 scripts/evol-memory.py edms-link "$TEXT" 2>/dev/null
    fi

    echo "[hook] Failure captured: $LESSON_FILE"
fi
exit 0
