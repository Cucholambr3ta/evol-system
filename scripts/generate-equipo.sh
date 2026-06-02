#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
REGISTRY="$ROOT_DIR/prompts/agents/registry.json"
OUTPUT="$ROOT_DIR/docs/equipo.md"

echo "=== Generating equipo ==="

if [ ! -f "$REGISTRY" ]; then
    echo "ERROR: registry.json not found at $REGISTRY"
    exit 1
fi

python3 "$SCRIPT_DIR/validate-registry.py" --strict

python3 "$SCRIPT_DIR/_generate_equipo.py" "$ROOT_DIR"

echo "=== Done ==="