#!/usr/bin/env python3
"""Validate registry.json against schema."""
import json, sys, os
from jsonschema import validate, ValidationError

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_schema(name):
    with open(f"{REPO_ROOT}/prompts/agents/{name}") as f:
        return json.load(f)

def load_registry():
    with open(f"{REPO_ROOT}/prompts/agents/registry.json") as f:
        return json.load(f)

def main():
    strict = "--strict" in sys.argv

    try:
        schema = load_schema("registry.schema.json")
        registry = load_registry()
        validate(instance=registry, schema=schema)
    except ValidationError as e:
        print(f"[VALIDATE] FAIL: {e.message}")
        if strict:
            sys.exit(1)

    agents = registry.get("agents", [])
    print(f"[VALIDATE] {len(agents)} agents registered")

    core_count = sum(1 for a in agents if a.get("category") == "core")
    print(f"[VALIDATE] {core_count} core agents (expected: 16)")

    if core_count != 16 and strict:
        print("[VALIDATE] FAIL: Expected 16 core agents")
        sys.exit(1)

    ids = [a.get("id") for a in agents]
    if len(ids) != len(set(ids)):
        print("[VALIDATE] FAIL: Duplicate agent IDs")
        sys.exit(1)

    print("[VALIDATE] OK")
    sys.exit(0)

if __name__ == "__main__":
    main()