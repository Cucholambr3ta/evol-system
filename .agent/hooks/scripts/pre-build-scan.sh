#!/bin/bash
# Hook: pre-build scan — escanea codigo antes de gate Build (Fase 4).
# Perfil: strict. Bloquea si CRITICAL. Advierte si HIGH.
# No-op si evol-scan.py no existe.
set -eu

SCRIPTS_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/../../.." && pwd )/scripts"
PROJECT_DIR="${PWD}"

if [ ! -f "$SCRIPTS_DIR/evol-scan.py" ]; then
  exit 0
fi

OUTFILE="${PROJECT_DIR}/.evol/qa/scan-results.json"
mkdir -p "$(dirname "$OUTFILE")" 2>/dev/null || true

echo "[evol-hook] pre-build scan en: $PROJECT_DIR" >&2
python3 "$SCRIPTS_DIR/evol-scan.py" source "$PROJECT_DIR" --output "$OUTFILE" 2>/dev/null
RC=$?

# RC=2 → CRITICAL encontrado → bloquear
# RC=1 → HIGH encontrado → solo advertir (a menos que EVOL_SEC_BLOCK_ON_HIGH=1)
if [ "$RC" -eq 2 ]; then
  echo "[evol-hook] BLOQUEADO: vulnerabilidades CRITICAL encontradas. Ver .evol/qa/scan-results.json" >&2
  exit 2
fi
if [ "$RC" -eq 1 ] && [ "${EVOL_SEC_BLOCK_ON_HIGH:-0}" = "1" ]; then
  echo "[evol-hook] BLOQUEADO (modo estricto): vulnerabilidades HIGH encontradas." >&2
  exit 2
fi
if [ "$RC" -eq 1 ]; then
  echo "[evol-hook] WARN: vulnerabilidades HIGH encontradas. Ver .evol/qa/scan-results.json" >&2
fi
exit 0
