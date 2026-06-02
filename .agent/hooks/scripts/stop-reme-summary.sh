#!/bin/bash
# Hook: stop:reme-summary — persiste sesion en memory/YYYY-MM-DD.md via evol-memory.py nativo.
# Perfil: minimal+. Requiere EVOL_MEMORY=1. Sin dependencias externas.
# No-op si EVOL_MEMORY != 1. Exit 0 siempre (no bloquea cierre de sesion).
set -eu

if [ "${EVOL_MEMORY:-0}" != "1" ]; then
  exit 0
fi

SCRIPTS_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/../../.." && pwd )/scripts"
PROJECT_DIR="${PWD}"

if [ ! -f "$SCRIPTS_DIR/evol-memory.py" ]; then
  echo "[evol-memory] WARN: evol-memory.py no encontrado" >&2
  exit 0
fi

# El evento Stop puede proveer JSON de mensajes via stdin — guardarlo en tmp
TMPFILE=$(mktemp /tmp/evol-memory-XXXXXX.jsonl 2>/dev/null || echo "")
if [ -n "$TMPFILE" ]; then
  cat > "$TMPFILE" 2>/dev/null || true
  if [ -s "$TMPFILE" ]; then
    python3 "$SCRIPTS_DIR/evol-memory.py" --project "$PROJECT_DIR" summarize --messages "$TMPFILE" &
  else
    python3 "$SCRIPTS_DIR/evol-memory.py" --project "$PROJECT_DIR" summarize &
  fi
  rm -f "$TMPFILE"
else
  python3 "$SCRIPTS_DIR/evol-memory.py" --project "$PROJECT_DIR" summarize &
fi

# gc de tool_result/ vencidos (async, en background)
python3 "$SCRIPTS_DIR/evol-memory.py" --project "$PROJECT_DIR" gc &

exit 0
