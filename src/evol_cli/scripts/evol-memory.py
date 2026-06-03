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

def main():
    parser = argparse.ArgumentParser(description="Evol-DD Memory Engine")
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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()