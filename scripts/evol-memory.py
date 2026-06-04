#!/usr/bin/env python3
"""Evol-DD Memory Engine — Conversational memory, stdlib only."""
import os, sys, json, time, argparse
from datetime import datetime, timedelta
from pathlib import Path
from _evol_common import get_logger, get_provider

logger = get_logger("memory")

MEMORY_DIR = "memory"
AGENT_MEMORY_FILE = "AGENT_MEMORY.md"
DIALOG_DIR = "dialog"
TOOL_RESULT_DIR = "tool_result"
COMPACT_THRESHOLD = int(os.environ.get("EVOL_MEMORY_COMPACT_THRESHOLD", 90000))
COMPACT_RESERVE = int(os.environ.get("EVOL_MEMORY_COMPACT_RESERVE", 10000))
TOOL_TTL_DAYS = int(os.environ.get("EVOL_MEMORY_TOOL_TTL_DAYS", 3))

def load():
    """Load session context (SessionStart hook)."""
    print("=== Memory Load ===")

    if os.path.exists(AGENT_MEMORY_FILE):
        print("--- AGENT_MEMORY.md ---")
        with open(AGENT_MEMORY_FILE) as f:
            print(f.read())

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    journal_path = os.path.join(MEMORY_DIR, f"{yesterday}.md")

    if os.path.exists(journal_path):
        print(f"--- Journal: {yesterday} ---")
        with open(journal_path) as f:
            print(f.read())

    print("===================")

def summarize(messages_file=None):
    """Persist session to journal (Stop hook)."""
    today = datetime.now().strftime("%Y-%m-%d")
    journal_path = os.path.join(MEMORY_DIR, f"{today}.md")

    os.makedirs(MEMORY_DIR, exist_ok=True)

    messages = []
    if messages_file and os.path.exists(messages_file):
        with open(messages_file) as f:
            for line in f:
                messages.append(json.loads(line))

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    entry = f"""
## Sesion {timestamp}

### Factual Memory
- Date: {today}
- Session duration: {len(messages)} messages
- Active project: See memoria.md

### Reflections & Logic
[Session summary extracted]

"""

    if os.path.exists(journal_path):
        with open(journal_path, "a") as f:
            f.write(entry)
    else:
        with open(journal_path, "w") as f:
            f.write(f"# {today}\n{entry}")

    total_tokens = sum(len(m.get("content", "")) for m in messages)
    if total_tokens > COMPACT_THRESHOLD:
        compact(messages_file)

    print(f"[OK] Session persisted to {journal_path}")

def compact(messages_file=None):
    """Compact long history into structured summary."""
    if not messages_file or not os.path.exists(messages_file):
        return

    provider = get_provider()

    messages = []
    with open(messages_file) as f:
        for line in f:
            messages.append(json.loads(line))

    truncated = messages[-100:]

    summary_prompt = f"Summarize this session into structured format:\nGoal:\nProgress:\nKey Decisions:\nNext Steps:\nCritical Context:"

    if provider.__class__.__name__ == "MockProvider":
        summary = "[mock summary — requires real LLM for actual summarization]"
    else:
        result = provider.complete(summary_prompt, max_tokens=500)
        summary = result["content"]

    with open(AGENT_MEMORY_FILE, "w") as f:
        f.write(f"# Agent Memory\n\n## Last Compact: {datetime.now().isoformat()}\n\n{summary}\n")

    print(f"[OK] Memory compacted to {AGENT_MEMORY_FILE}")

def search(query, max_results=5):
    """BM25-style search over memory."""
    results = []

    if os.path.exists(AGENT_MEMORY_FILE):
        with open(AGENT_MEMORY_FILE) as f:
            content = f.read()
            if query.lower() in content.lower():
                results.append(("AGENT_MEMORY.md", content[:200]))

    for journal in sorted(Path(MEMORY_DIR).glob("*.md")):
        with open(journal) as f:
            content = f.read()
            if query.lower() in content.lower():
                results.append((str(journal), content[:200]))

    for i, (source, snippet) in enumerate(results[:max_results]):
        print(f"[{i+1}] {source}")
        print(f"    {snippet[:100]}...")

    print(f"[INFO] Found {len(results)} results")

def gc(days=None):
    """Purge expired tool results."""
    if days is None:
        days = TOOL_TTL_DAYS

    cutoff = datetime.now() - timedelta(days=days)
    removed = 0

    if os.path.exists(TOOL_RESULT_DIR):
        for f in os.listdir(TOOL_RESULT_DIR):
            path = os.path.join(TOOL_RESULT_DIR, f)
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                os.remove(path)
                removed += 1

    print(f"[GC] Removed {removed} expired tool results")

def stats():
    """Show memory system stats."""
    print("=== Memory Stats ===")

    journal_count = len(list(Path(MEMORY_DIR).glob("*.md")))
    print(f"Journals: {journal_count}")

    if os.path.exists(AGENT_MEMORY_FILE):
        size = os.path.getsize(AGENT_MEMORY_FILE)
        print(f"AGENT_MEMORY.md: {size} bytes")
    else:
        print("AGENT_MEMORY.md: not found")

    dialog_count = len(list(Path(DIALOG_DIR).glob("*.jsonl")))
    print(f"Dialog files: {dialog_count}")

    if os.path.exists(TOOL_RESULT_DIR):
        tool_count = len(os.listdir(TOOL_RESULT_DIR))
        print(f"Tool results: {tool_count}")

    print("===================")

def _sprint_num_str(sprint) -> str:
    """Normaliza sprint a 2 dígitos: 1 → '01', '3' → '03', '12' → '12'."""
    return f"{int(sprint):02d}"


def _update_lecciones_index(index_path: Path, sprint: str, today: str) -> None:
    entry = f"| sprint-{sprint} | [sprint-{sprint}.md](sprint-{sprint}.md) | {today} |"
    header = (
        "# INDEX — Lecciones por Sprint\n\n"
        "> Indice de lecciones separadas por sprint. Categorias: ARQUITECTURA, SEGURIDAD, DOMINIO, TESTING, DEVOPS, PROCESO, HERRAMIENTAS.\n\n"
        "| Sprint | Archivo | Fecha cierre |\n"
        "|--------|---------|-------------|\n"
    )
    if not index_path.exists():
        index_path.write_text(header + entry + "\n", encoding="utf-8")
        return
    content = index_path.read_text(encoding="utf-8")
    marker = f"| sprint-{sprint} |"
    if marker in content:
        lines = [entry if l.startswith(marker) else l for l in content.splitlines()]
        index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        index_path.write_text(content.rstrip("\n") + "\n" + entry + "\n", encoding="utf-8")


def sprint_close(sprint, project=".", memoria_content=None, lecciones_content=None, force=False):
    """Cierra sprint: crea acuerdos/memoria/sprint-NN.md + acuerdos/lecciones/sprint-NN.md."""
    s = _sprint_num_str(sprint)
    today = datetime.now().strftime("%Y-%m-%d")
    acuerdos = Path(project) / "acuerdos"
    mem_dir = acuerdos / "memoria"
    les_dir = acuerdos / "lecciones"
    mem_dir.mkdir(parents=True, exist_ok=True)
    les_dir.mkdir(parents=True, exist_ok=True)

    sprint_mem = mem_dir / f"sprint-{s}.md"
    sprint_les = les_dir / f"sprint-{s}.md"

    if sprint_mem.exists() and not force:
        print(f"[evol-memory] acuerdos/memoria/sprint-{s}.md ya existe. Usar --force para sobreescribir.")
    else:
        content = memoria_content or f"# Memoria Sprint {s} — {today}\n\n## Hitos\n\n-\n\n## Bloqueos\n\n-\n\n## Proxima sesion\n\n-\n"
        sprint_mem.write_text(content, encoding="utf-8")
        print(f"[evol-memory] ✓ acuerdos/memoria/sprint-{s}.md creado.")

    if sprint_les.exists() and not force:
        print(f"[evol-memory] acuerdos/lecciones/sprint-{s}.md ya existe. Usar --force para sobreescribir.")
    else:
        content = lecciones_content or f"# Lecciones Sprint {s} — {today}\n\n> Formato: CATEGORIA / Contexto / Problema / Causa raiz / Leccion / Aplica a.\n\n"
        sprint_les.write_text(content, encoding="utf-8")
        print(f"[evol-memory] ✓ acuerdos/lecciones/sprint-{s}.md creado.")

    _update_lecciones_index(les_dir / "INDEX.md", s, today)
    print(f"[evol-memory] ✓ acuerdos/lecciones/INDEX.md actualizado.")

    memory_md = mem_dir / "MEMORY.md"
    if not memory_md.exists():
        memory_md.write_text(
            "# MEMORY.md — Hechos persistentes del proyecto\n\n"
            "> Solo hechos duraderos, no log temporal.\n\n"
            "## Decisiones clave\n\n-\n\n## Convenciones\n\n-\n\n## Riesgos activos\n\n-\n",
            encoding="utf-8",
        )
        print("[evol-memory] ✓ acuerdos/memoria/MEMORY.md inicializado.")


def main():
    parser = argparse.ArgumentParser(description="Evol-DD Memory Engine")
    # Arg global --project ANTES del subcomando
    parser.add_argument("--project", default=".", help="Directorio del proyecto (default: $PWD)")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("load", help="Load session context (SessionStart)")
    sub.add_parser("stats", help="Show memory stats")

    p = sub.add_parser("summarize", help="Persist session to journal (Stop)")
    p.add_argument("--messages", help="JSONL messages file")

    p = sub.add_parser("compact", help="Compact long history")
    p.add_argument("--messages", help="JSONL messages file")

    p = sub.add_parser("search", help="Search memory")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=5)

    p = sub.add_parser("gc", help="Garbage collect expired tool results")
    p.add_argument("--days", type=int, default=TOOL_TTL_DAYS)

    p = sub.add_parser("sprint-close", help="Cierra sprint: crea acuerdos/memoria/sprint-NN.md + lecciones")
    p.add_argument("--sprint", required=True, help="Numero de sprint (1, '01', etc.)")
    p.add_argument("--memoria", default=None, help="Contenido para memoria/sprint-NN.md")
    p.add_argument("--lecciones", default=None, help="Contenido para lecciones/sprint-NN.md")
    p.add_argument("--force", action="store_true", help="Sobreescribir si ya existe")

    args = parser.parse_args()

    if args.cmd == "load":
        load()
    elif args.cmd == "summarize":
        summarize(args.messages)
    elif args.cmd == "compact":
        compact(args.messages)
    elif args.cmd == "search":
        search(args.query, args.max)
    elif args.cmd == "gc":
        gc(args.days)
    elif args.cmd == "stats":
        stats()
    elif args.cmd == "sprint-close":
        sprint_close(
            sprint=args.sprint,
            project=args.project,
            memoria_content=args.memoria,
            lecciones_content=args.lecciones,
            force=args.force,
        )
        if args.json:
            import json as _json
            s = _sprint_num_str(args.sprint)
            print(_json.dumps({"ok": True, "sprint": s}))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()