#!/bin/bash
# Hook: session:start:reme-load — carga MEMORY.md + journal anterior via evol-memory.py nativo.
# Perfil: minimal+. Requiere EVOL_MEMORY=1. Sin dependencias externas.
# No-op si EVOL_MEMORY != 1. Exit 0 siempre.
set -eu

if [ "${EVOL_MEMORY:-0}" != "1" ]; then
  exit 0
fi

SCRIPTS_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/../../.." && pwd )/scripts"
PROJECT_DIR="${PWD}"

if [ ! -f "$SCRIPTS_DIR/evol-memory.py" ]; then
  echo "[evol-memory] WARN: evol-memory.py no encontrado en $SCRIPTS_DIR" >&2
  exit 0
fi

python3 "$SCRIPTS_DIR/evol-memory.py" --project "$PROJECT_DIR" load
exit 0
