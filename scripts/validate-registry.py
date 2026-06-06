#!/usr/bin/env python3
"""Validate registry.json against schema and business rules."""
import json, sys, os
from jsonschema import validate, ValidationError

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_schema(name):
    with open(f"{REPO_ROOT}/prompts/agents/{name}") as f:
        return json.load(f)

def load_registry():
    with open(f"{REPO_ROOT}/prompts/agents/registry.json") as f:
        return json.load(f)

def collect_skills():
    skills_dir = f"{REPO_ROOT}/skills"
    if os.path.isdir(skills_dir):
        return {d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))}
    return set()

def validate_invariants(agents, skills, strict=False):
    errors = []
    seen_ids = []
    seen_names = []

    for agent in agents:
        aid = agent.get("id")
        name = agent.get("name")

        if aid in seen_ids:
            errors.append(f"[INVARIANT] Duplicate ID: {aid}")
        seen_ids.append(aid)

        if name in seen_names:
            errors.append(f"[INVARIANT] Duplicate name: {name}")
        seen_names.append(name)

        retired = agent.get("retired")
        retired_at = agent.get("retired_at")

        if retired in (False, None) and retired_at is not None:
            errors.append(f"[INVARIANT] Agent {name}: retired=false/null but has retired_at={retired_at}")

        if retired is True and retired_at is None:
            errors.append(f"[INVARIANT] Agent {name}: retired=true but no retired_at")

        if agent.get("category") == "core":
            if "file" not in agent:
                errors.append(f"[INVARIANT] Core agent {name}: missing 'file' field")
            if "triggers" not in agent:
                errors.append(f"[INVARIANT] Core agent {name}: missing 'triggers' field")

    return errors

def check_skill_references(agents, skills):
    warnings = []
    for agent in agents:
        name = agent.get("name")
        for skill in agent.get("skills", []):
            skill_base = skill.replace("skill-", "").replace("_", "-")
            matched = any(skill_base == s.replace("_", "-") for s in skills)
            if not matched:
                warnings.append(f"[WARNING] Agent {name}: skill '{skill}' not found in skills/")
    return warnings

def main():
    strict = "--strict" in sys.argv

    try:
        schema = load_schema("registry.schema.json")
        registry = load_registry()
        validate(instance=registry, schema=schema)
        print("[SCHEMA] OK")
    except ValidationError as e:
        print(f"[SCHEMA] FAIL: {e.message}")
        if strict:
            sys.exit(1)

    agents = registry.get("agents", [])
    print(f"[REGISTRY] {len(agents)} agents registered")

    core_count = sum(1 for a in agents if a.get("category") == "core")
    print(f"[REGISTRY] {core_count} core agents (expected: 17)")

    if core_count != 17:
        print("[REGISTRY] FAIL: Expected 18 core agents")
        if strict:
            sys.exit(1)

    ids = [a.get("id") for a in agents]
    if len(ids) != len(set(ids)):
        print("[REGISTRY] FAIL: Duplicate agent IDs")
        sys.exit(1)

    skills = collect_skills()
    print(f"[SKILLS] {len(skills)} skills found: {sorted(skills)}")

    for w in check_skill_references(agents, skills):
        print(w)

    invariant_errors = validate_invariants(agents, skills, strict)
    if invariant_errors:
        for err in invariant_errors:
            print(err)
        if strict:
            sys.exit(1)

    ephemeral_count = sum(1 for a in agents if a.get("category") == "ephemeral")
    print(f"[REGISTRY] {ephemeral_count} ephemeral agents")

    print("[VALIDATE] OK")
    sys.exit(0)

if __name__ == "__main__":
    main()