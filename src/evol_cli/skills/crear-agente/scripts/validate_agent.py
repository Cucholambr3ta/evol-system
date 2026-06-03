#!/usr/bin/env python3
"""Valida que un agente recien creado cumpla los requisitos de Evol-DD.

Uso: python3 validate_agent.py <agent_file.md> [--registry registry.json]
Exit 0 = OK | Exit 1 = error
"""
import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_FRONTMATTER = ["name", "description", "vibe"]
REQUIRED_SECTIONS = ["##"]  # Al menos una seccion H2


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm_text = text[3:end].strip()
    result = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            result[k.strip()] = v.strip()
    return result


def validate_agent(agent_path: Path, registry_path: Path | None) -> list[str]:
    errors = []
    if not agent_path.exists():
        return [f"Archivo no encontrado: {agent_path}"]

    text = agent_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)

    # Frontmatter obligatorio
    for field in REQUIRED_FRONTMATTER:
        if field not in fm or not fm[field]:
            errors.append(f"Frontmatter faltante o vacio: '{field}'")

    # Sin emojis en el body (emojis en frontmatter son OK)
    body = text[text.find("---", 3) + 3:] if "---" in text[3:] else text
    emoji_pattern = re.compile(
        "[\U0001F000-\U0001FAFF\U00002600-\U000027BF]"
    )
    if emoji_pattern.search(body):
        errors.append("Emojis detectados en el body del agente (violan DOC_STANDARD.md)")

    # Al menos una seccion H2
    if "## " not in body:
        errors.append("Sin secciones H2 — el agente debe tener estructura minima")

    # Description no vaga
    desc = fm.get("description", "")
    if len(desc) < 30:
        errors.append(f"description muy corta ({len(desc)} chars) — ser mas especifico")

    # Verificar en registry si se paso
    if registry_path and registry_path.exists():
        reg = json.loads(registry_path.read_text(encoding="utf-8"))
        agent_name = fm.get("name", "").lower().replace(" ", "-")
        found = any(
            a.get("prompt_file", "").endswith(agent_path.name)
            for a in reg.get("agents", [])
        )
        if not found:
            errors.append(
                f"Agente '{agent_path.name}' no encontrado en registry.json — "
                "añadir entry antes de usar"
            )

    return errors


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("agent_file", type=Path)
    p.add_argument("--registry", type=Path, default=None)
    args = p.parse_args()

    errors = validate_agent(args.agent_file, args.registry)
    if errors:
        print(f"[crear-agente] ERRORES en {args.agent_file.name}:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"[crear-agente] OK — {args.agent_file.name} valido")
        sys.exit(0)


if __name__ == "__main__":
    main()
