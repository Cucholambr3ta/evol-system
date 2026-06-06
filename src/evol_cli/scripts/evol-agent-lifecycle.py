#!/usr/bin/env python3
"""Evol-DD Agent Lifecycle — Ephemeral agent management."""
import os, sys, json, argparse, hashlib, shutil, subprocess
from datetime import datetime, timedelta

try:
    from evol_cli.scripts._evol_common import get_logger, get_data_dir, memoria_persistente_safe, save_json, load_json
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _evol_common import get_logger, get_data_dir, memoria_persistente_safe, save_json, load_json

logger = get_logger("agent-lifecycle")

REGISTRY_PATH = "prompts/agents/registry.json"
EPHEMERAL_DIR = "prompts/agents/ephemeral"
RETIRED_DIR = ".evol/agents/retired"
RETENTION_DAYS = 90

def get_registry():
    if not os.path.exists(REGISTRY_PATH):
        return {"agents": []}
    return load_json(REGISTRY_PATH)

def save_registry(registry):
    save_json(REGISTRY_PATH, registry)

def sha256_prompt(prompt_text):
    return hashlib.sha256(prompt_text.encode()).hexdigest()

def create_agent(name, task, expires_after=30):
    """Create ephemeral agent from template."""
    os.makedirs(EPHEMERAL_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}-{name}.md"
    filepath = os.path.join(EPHEMERAL_DIR, filename)

    template_path = "templates/agent.template.md"
    if not os.path.exists(template_path):
        template_path = os.path.join(get_data_dir(), "templates/agent.template.md")

    if not os.path.exists(template_path):
        print(f"[ERROR] Template not found: {template_path}")
        sys.exit(1)

    with open(template_path) as f:
        template = f.read()

    agent_content = template.replace("{{agent_name}}", name)
    agent_content = agent_content.replace("{{descripcion_una_linea}}", task[:100])
    agent_content = agent_content.replace("{{tarea_especifica}}", task)
    agent_content = agent_content.replace("{{dias}}", str(expires_after))
    agent_content = agent_content.replace("{{ISO8601}}", datetime.now().isoformat())
    agent_content = agent_content.replace("{{que_puede_y_no_puede_hacer_este_agente}}",
        f"Especializado en: {task}. No puede modificar gobernanza.")
    agent_content = agent_content.replace("{{referencias_a_DOMAIN.md_memoria.md_lecciones.md_relevantes}}",
        "Referencia: memoria.md, lecciones.md del proyecto actual.")

    frontmatter = f"""---
name: {name}
description: {task[:100]}
category: ephemeral
created_for_task: {task}
expires_after_days: {expires_after}
created_at: {datetime.now().isoformat()}
---
"""
    full_content = frontmatter + agent_content

    with open(filepath, "w") as f:
        f.write(full_content)

    registry = get_registry()
    agent_id = name.lower().replace(" ", "-")
    registry["agents"].append({
        "id": agent_id,
        "name": name,
        "category": "ephemeral",
        "description": task,
        "prompt_file": filepath,
        "ephemeral": True,
        "created_for_task": task,
        "expires_after_days": expires_after,
        "created_at": datetime.now().isoformat(),
        "retired": False,
        "sessions_used": 0
    })
    save_registry(registry)

    memoria_persistente_safe("index", "--path", EPHEMERAL_DIR)



    logger.info(f"Created: {name} -> {filepath}")
    print(f"[OK] Agent created: {name} (expires in {expires_after} days)")

def invoke_agent(name):
    """Mark agent as invoked in this session."""
    registry = get_registry()
    agent_id = name.lower().replace(" ", "-")

    for agent in registry["agents"]:
        if agent.get("id") == agent_id or agent.get("name") == name:
            agent["sessions_used"] = agent.get("sessions_used", 0) + 1
            save_registry(registry)
            print(f"[OK] Agent invoked: {agent['name']}")
            print(f"[INFO] Sessions used: {agent['sessions_used']}")
            return

    print(f"[ERROR] Agent not found: {name}")
    sys.exit(1)

def retire_agent(name):
    """Retire agent: remove .md, archive snapshot."""
    registry = get_registry()
    agent_id = name.lower().replace(" ", "-")

    agent = None
    for a in registry["agents"]:
        if a.get("id") == agent_id or a.get("name") == name:
            agent = a
            break

    if not agent:
        print(f"[ERROR] Agent not found: {name}")
        sys.exit(1)

    prompt_content = ""
    prompt_file = agent.get("prompt_file")
    if prompt_file and os.path.exists(prompt_file):
        with open(prompt_file) as f:
            prompt_content = f.read()
        os.remove(prompt_file)
    else:
        for f in os.listdir(EPHEMERAL_DIR):
            if name in f:
                filepath = os.path.join(EPHEMERAL_DIR, f)
                with open(filepath) as fh:
                    prompt_content = fh.read()
                os.remove(filepath)
                break

    os.makedirs(RETIRED_DIR, exist_ok=True)
    snapshot = {
        "name": agent["name"],
        "prompt": prompt_content,
        "prompt_sha256": sha256_prompt(prompt_content) if prompt_content else "",
        "created_at": agent.get("created_at"),
        "retired_at": datetime.now().isoformat(),
        "invocation_log": [],
        "sessions_used": agent.get("sessions_used", 0),
        "created_for_task": agent.get("created_for_task")
    }

    snapshot_path = os.path.join(RETIRED_DIR, f"{agent_id}.json")
    save_json(snapshot_path, snapshot)

    agent["retired"] = True
    agent["retired_at"] = datetime.now().isoformat()
    agent["prompt_file"] = None
    save_registry(registry)

    logger.info(f"Retired: {name} -> {snapshot_path}")
    print(f"[OK] Agent retired: {name}")
    print(f"[INFO] Snapshot archived: {snapshot_path}")

def recall_agent(name, force=False):
    """Recall retired agent from snapshot."""
    registry = get_registry()
    agent_id = name.lower().replace(" ", "-")

    snapshot_path = os.path.join(RETIRED_DIR, f"{agent_id}.json")
    if not os.path.exists(snapshot_path):
        print(f"[ERROR] Snapshot not found: {snapshot_path}")
        sys.exit(1)

    snapshot = load_json(snapshot_path)

    if not force and snapshot.get("prompt_sha256"):
        computed = sha256_prompt(snapshot["prompt"])
        if computed != snapshot["prompt_sha256"]:
            print(f"[ERROR] Snapshot integrity check FAILED")
            print(f"[ERROR] Expected: {snapshot['prompt_sha256']}")
            print(f"[ERROR] Computed: {computed}")
            print(f"[HINT] Use --force to override")
            sys.exit(1)

    os.makedirs(EPHEMERAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}-{name}.md"
    filepath = os.path.join(EPHEMERAL_DIR, filename)

    with open(filepath, "w") as f:
        f.write(snapshot["prompt"])

    for agent in registry["agents"]:
        if agent.get("id") == agent_id:
            agent["retired"] = False
            agent["recalled"] = True
            agent["recalled_at"] = datetime.now().isoformat()
            agent["prompt_file"] = filepath
            agent["sessions_used"] = 0
            break

    save_registry(registry)

    memoria_persistente_safe("index", "--path", EPHEMERAL_DIR)

    recall_type = "COMPLETO" if memoria_persistente_safe("search", name) else "BASICO"
    logger.info(f"Recalled: {name} (type: {recall_type})")
    if recall_type == "COMPLETO":
        print(f"[OK] Agent recalled: {name}")
        print(f"[INFO] Recall type: COMPLETO (JSON + semantic)")
    else:
        print(f"[OK] Agent recalled: {name}")
        print(f"[INFO] Recall type: BASICO (JSON only)")

def gc_agents():
    """Garbage collect expired agents."""
    registry = get_registry()
    now = datetime.now()
    collected = 0

    for agent in registry["agents"]:
        if agent.get("ephemeral") and not agent.get("retired"):
            expires = agent.get("expires_after_days")
            created = agent.get("created_at")

            if expires and created:
                created_dt = datetime.fromisoformat(created)
                expiry_dt = created_dt + timedelta(days=expires)

                if now > expiry_dt:
                    retire_agent(agent["name"])
                    collected += 1

    print(f"[GC] Collected {collected} expired agents")

def list_agents(filter_type="all"):
    """List agents by filter."""
    registry = get_registry()
    count = 0

    for agent in registry["agents"]:
        cat = agent.get("category", "unknown")

        if filter_type == "all":
            pass
        elif filter_type == "ephemeral" and cat != "ephemeral":
            continue
        elif filter_type == "retired" and not agent.get("retired"):
            continue
        elif filter_type == "core" and cat != "core":
            continue

        status = "RETIRED" if agent.get("retired") else "ACTIVE"
        print(f"[{status}] {agent.get('name')} ({cat})")
        count += 1

    print(f"[INFO] Total: {count}")

def main():
    parser = argparse.ArgumentParser(description="Evol-DD Agent Lifecycle")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("create", help="Create ephemeral agent")
    p.add_argument("--name", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--expires-after", type=int, default=30)

    p = sub.add_parser("invoke", help="Mark agent as invoked")
    p.add_argument("name")

    p = sub.add_parser("retire", help="Retire agent")
    p.add_argument("name")

    p = sub.add_parser("recall", help="Recall retired agent")
    p.add_argument("name")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("gc", help="Garbage collect expired agents")

    p = sub.add_parser("list", help="List agents")
    p.add_argument("--ephemeral", action="store_true")
    p.add_argument("--retired", action="store_true")
    p.add_argument("--core", action="store_true")
    p.add_argument("--all", action="store_true")

    args = parser.parse_args()

    if args.cmd == "create":
        create_agent(args.name, args.task, args.expires_after)
    elif args.cmd == "invoke":
        invoke_agent(args.name)
    elif args.cmd == "retire":
        retire_agent(args.name)
    elif args.cmd == "recall":
        recall_agent(args.name, args.force)
    elif args.cmd == "gc":
        gc_agents()
    elif args.cmd == "list":
        filter_type = "all"
        if args.ephemeral:
            filter_type = "ephemeral"
        elif args.retired:
            filter_type = "retired"
        elif args.core:
            filter_type = "core"
        list_agents(filter_type)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()