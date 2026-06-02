#!/usr/bin/env python3
import json
from datetime import datetime
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."

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
            status = "retired" if agent.get("retired") in (True, "true") else "active"
            f.write(f"| `{agent['name']}` | {agent['description']} | {status} |\n")
    else:
        f.write("No ephemeral agents currently.\n")

print(f"Generated {ROOT}/docs/equipo.md")