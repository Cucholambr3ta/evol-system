#!/usr/bin/env bash
# PostToolUse hook: Index edits to acuerdos/ into EDMS + v2 + auto-update graph
# Triggered after every edit to .md files in acuerdos/ AND code files

EDMS_INDEX_FILE="${EDMS_INDEX_FILE:-.evol/.edms-last-edit}"
PROJECT="${EVOL_PROJECT:-.}"

# Get the file that was edited from environment or stdin
EDITED_FILE="${CLAUDE_FILE_PATH:-$1}"

# ── Code file indexing ────────────────────────────────────────────────────
CODE_EXTENSIONS=".py|.js|.jsx|.ts|.tsx"
if [[ "$EDITED_FILE" =~ \.($CODE_EXTENSIONS)$ ]]; then
    if command -v python3 &>/dev/null; then
        # Incremental code index (only changed files)
        python3 scripts/evol_code_indexer.py index "$PROJECT" 2>/dev/null &
        echo "{\"code_indexed\": \"$EDITED_FILE\", \"agent\": \"hook:post-edit\"}" > "$EDMS_INDEX_FILE"
    fi
    exit 0
fi

# ── Acuerdos file indexing ────────────────────────────────────────────────
if [[ "$EDITED_FILE" == acuerdos/*.md && "$EDITED_FILE" == *.md ]]; then
    if command -v python3 &>/dev/null; then
        # Extract tipo from path
        TIPO="artefacto"
        if [[ "$EDITED_FILE" == *"/memoria/"* ]]; then
            TIPO="decision"
        elif [[ "$EDITED_FILE" == *"/lecciones/"* ]]; then
            TIPO="leccion"
        elif [[ "$EDITED_FILE" == *"/research/"* ]]; then
            TIPO="artefacto"
        elif [[ "$EDITED_FILE" == *"/discovery/"* ]]; then
            TIPO="artefacto"
        fi

        # Extract sprint from path if present
        SPRINT=""
        if [[ "$EDITED_FILE" =~ sprint-([0-9]+) ]]; then
            SPRINT="${BASH_REMATCH[1]}"
        fi

        # Extract disciplinas from file content (first 500 chars)
        DISCIPLINAS=""
        if [[ "$EDITED_FILE" == *"/research/"* ]] || [[ "$EDITED_FILE" == *"/discovery/"* ]]; then
            DISCIPLINAS=$(head -c 500 "$EDITED_FILE" 2>/dev/null | grep -oE '(DDD|TDD|BDD|SecDD|DevDD|DocDD|APIDD)' | head -3 | tr '\n' ',' | sed 's/,$//')
        fi

        TEXT=$(head -c 2000 "$EDITED_FILE" 2>/dev/null)
        if [ -n "$TEXT" ]; then
            # v1: Build command with optional args
            CMD="python3 scripts/evol-memory.py --project=\"$PROJECT\" edms-index \"$TEXT\" --tipo=\"$TIPO\" --agent=\"hook:post-edit\""
            [ -n "$SPRINT" ] && CMD="$CMD --sprint=\"$SPRINT\""
            [ -n "$DISCIPLINAS" ] && CMD="$CMD --disciplinas=\"$DISCIPLINAS\""

            eval $CMD 2>/dev/null
            
            # v2: Verbatim storage + entity extraction + auto-linking
            python3 scripts/evol-memory.py edms-store "$TEXT" --tipo="$TIPO" 2>/dev/null
            python3 scripts/evol-memory.py edms-extract "$TEXT" 2>/dev/null
            python3 scripts/evol-memory.py edms-link "$TEXT" 2>/dev/null
            
            echo "{\"indexed\": \"$EDITED_FILE\", \"tipo\": \"$TIPO\", \"sprint\": \"$SPRINT\", \"v2\": true}" > "$EDMS_INDEX_FILE"

            # Emit file event for real-time tracking
            python3 -c "
from evol_traces import emit_file_event
emit_file_event('$PROJECT', '$EDITED_FILE', action='modified', agent='hook:post-edit')
" 2>/dev/null || true
        fi
    fi
fi
exit 0
