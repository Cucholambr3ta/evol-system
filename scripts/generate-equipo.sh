#!/bin/bash
# generate-equipo.sh - Generar equipo de agentes desde registry.json

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

python3 << 'PYEOF'
import json
from datetime import datetime
import sys

sys.path.insert(0, "/home/alejandro/Documentos/Desarrollos/personal/evol-dd")
ROOT = "/home/alejandro/Documentos/Desarrollos/personal/evol-dd"

with open(f"{ROOT}/prompts/agents/registry.json") as f:
    data = json.load(f)

with open(f"{ROOT}/docs/equipo.md", "w") as f:
    f.write("# Equipo de Agentes\n\n")
    f.write(f"Generado: {datetime.now().isoformat()}\n\n")
    f.write("---\n\n")
    
    f.write("## Core Agents (16)\n\n")
    f.write("| ID | Agent | Description |\n")
    f.write("|----|-------|-------------|\n")
    
    for agent in data["agents"]:
        if agent["category"] == "core":
            f.write(f"| {agent['id']} | `{agent['name']}` | {agent['description']} |\n")
    
    f.write("\n## Ephemeral Agents\n\n")
    ephemeral = [a for a in data["agents"] if a["category"] == "ephemeral"]
    if ephemeral:
        f.write("| Name | Description | Status |\n")
        f.write("|------|-------------|--------|\n")
        for agent in ephemeral:
            status = "retired" if agent["retired"] else "active"
            f.write(f"| `{agent['name']}` | {agent['description']} | {status} |\n")
    else:
        f.write("No ephemeral agents currently.\n")

print(f"Generated {ROOT}/docs/equipo.md")
PYEOF

echo "=== Done ==="