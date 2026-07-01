#!/usr/bin/env python3
"""EDMS Real-Time Event Emission — NDJSON traces.

Stdlib-only emitter that writes structured events to:
  .evol/traces/<session-id>.jsonl

Format per NFR-008:
  {"ts":"ISO8601","event":"name","session_id":"...","agent":"...","project":"...","data":{...}}

Usage:
  from evol_traces import emit, get_session_id
  emit("edms_index", project="evol-dd", data={"tipo": "decision", "doc_id": "a1b2"})
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Config ────────────────────────────────────────────────────────────────

TRACES_DIR = Path(os.environ.get("EVOL_TRACES_DIR", ".evol/traces"))
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 50
SESSION_ID_FILE = ".evol/.session-id"

# ── Session management ───────────────────────────────────────────────────

_session_id: str | None = None


def get_session_id() -> str:
    """Get or create session ID. Persists across calls in same process."""
    global _session_id
    if _session_id:
        return _session_id

    # Try to load existing session ID
    id_file = Path(SESSION_ID_FILE)
    if id_file.exists():
        try:
            _session_id = id_file.read_text().strip()
            if _session_id:
                return _session_id
        except Exception:
            pass

    # Generate new session ID
    _session_id = uuid.uuid4().hex[:12]
    try:
        id_file.parent.mkdir(parents=True, exist_ok=True)
        id_file.write_text(_session_id)
    except Exception:
        pass

    return _session_id


def set_session_id(sid: str) -> None:
    """Override session ID (for hooks that receive it from parent)."""
    global _session_id
    _session_id = sid
    try:
        Path(SESSION_ID_FILE).parent.mkdir(parents=True, exist_ok=True)
        Path(SESSION_ID_FILE).write_text(sid)
    except Exception:
        pass


# ── Trace file management ────────────────────────────────────────────────

def _get_trace_path(session_id: str | None = None) -> Path:
    """Get path to current trace file. Rotates if > MAX_FILE_SIZE."""
    sid = session_id or get_session_id()
    traces_dir = TRACES_DIR
    traces_dir.mkdir(parents=True, exist_ok=True)

    trace_file = traces_dir / f"{sid}.jsonl"

    # Rotate if too large
    if trace_file.exists() and trace_file.stat().st_size > MAX_FILE_SIZE:
        _rotate_trace(traces_dir, sid)

    return trace_file


def _rotate_trace(traces_dir: Path, session_id: str) -> None:
    """Rotate trace files: rename current to .1, .2, etc."""
    base = traces_dir / session_id
    for i in range(MAX_FILES - 1, 0, -1):
        src = base.with_suffix(f".{i}.jsonl")
        dst = base.with_suffix(f".{i + 1}.jsonl")
        if src.exists():
            if i + 1 >= MAX_FILES:
                src.unlink()
            else:
                src.rename(dst)

    # Rename current to .1
    current = base.with_suffix(".jsonl")
    if current.exists():
        current.rename(base.with_suffix(".1.jsonl"))


def _update_index(session_id: str, trace_path: Path) -> None:
    """Update index.json with session metadata."""
    index_path = TRACES_DIR / "index.json"
    try:
        if index_path.exists():
            index = json.loads(index_path.read_text())
        else:
            index = {}
    except Exception:
        index = {}

    index[session_id] = {
        "file": str(trace_path.name),
        "size": trace_path.stat().st_size if trace_path.exists() else 0,
        "updated": datetime.now(timezone.utc).isoformat(),
    }

    # Prune old entries
    if len(index) > MAX_FILES:
        sorted_keys = sorted(index.keys(), key=lambda k: index[k].get("updated", ""))
        for old_key in sorted_keys[:-MAX_FILES]:
            del index[old_key]

    try:
        index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False))
    except Exception:
        pass


# ── Core emit function ───────────────────────────────────────────────────

def emit(
    event: str,
    *,
    session_id: str | None = None,
    agent: str = "",
    project: str = "",
    data: dict[str, Any] | None = None,
) -> str | None:
    """Emit a structured event to NDJSON trace file.

    Args:
        event: Event name (e.g., "edms_index", "graph_node_created")
        session_id: Override session ID (default: auto-detected)
        agent: Agent name performing the action
        project: Project name
        data: Event-specific payload

    Returns:
        Path to trace file, or None on error
    """
    sid = session_id or get_session_id()

    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "session_id": sid,
    }

    if agent:
        record["agent"] = agent
    if project:
        record["project"] = project
    if data:
        record["data"] = data

    try:
        trace_path = _get_trace_path(sid)
        with open(trace_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        _update_index(sid, trace_path)
        return str(trace_path)
    except Exception:
        return None


# ── Convenience emitters ─────────────────────────────────────────────────

def emit_session_start(project: str = "", agent: str = "orchestrator") -> str | None:
    """Emit session start event."""
    return emit("session_start", agent=agent, project=project)


def emit_session_end(project: str = "", agent: str = "orchestrator") -> str | None:
    """Emit session end event."""
    return emit("session_end", agent=agent, project=project)


def emit_edms_index(
    project: str,
    tipo: str,
    doc_id: str,
    agent: str = "",
    **extra,
) -> str | None:
    """Emit EDMS index event."""
    data = {"tipo": tipo, "doc_id": doc_id}
    data.update(extra)
    return emit("edms_index", agent=agent, project=project, data=data)


def emit_edms_search(
    project: str,
    query: str,
    result_count: int,
    agent: str = "",
) -> str | None:
    """Emit EDMS search event."""
    return emit("edms_search", agent=agent, project=project, data={
        "query": query[:200],
        "result_count": result_count,
    })


def emit_graph_node(
    project: str,
    node_type: str,
    node_name: str,
    action: str = "created",
    agent: str = "",
) -> str | None:
    """Emit graph node event."""
    return emit(f"graph_node_{action}", agent=agent, project=project, data={
        "node_type": node_type,
        "node_name": node_name,
    })


def emit_graph_relation(
    project: str,
    source: str,
    relation: str,
    target: str,
    agent: str = "",
) -> str | None:
    """Emit graph relation event."""
    return emit("graph_relation_created", agent=agent, project=project, data={
        "source": source,
        "relation": relation,
        "target": target,
    })


def emit_file_event(
    project: str,
    file_path: str,
    action: str = "created",
    agent: str = "hook:post-edit",
) -> str | None:
    """Emit file event (created/modified)."""
    return emit(f"file_{action}", agent=agent, project=project, data={
        "file": file_path,
    })


def emit_agent_action(
    project: str,
    agent: str,
    action: str,
    **extra,
) -> str | None:
    """Emit agent action event (for loop detection)."""
    data = {"action": action}
    data.update(extra)
    return emit("agent_action", agent=agent, project=project, data=data)


def emit_gate_approved(
    project: str,
    phase: str,
    agent: str = "",
) -> str | None:
    """Emit gate approval event."""
    return emit("gate_approved", agent=agent, project=project, data={
        "phase": phase,
    })


def emit_error(
    project: str,
    error: str,
    context: str = "",
    agent: str = "",
) -> str | None:
    """Emit error event."""
    return emit("error", agent=agent, project=project, data={
        "error": error[:500],
        "context": context,
    })


# ── Code Graph emitters ──────────────────────────────────────────────────

def emit_code_index(
    project: str,
    files_indexed: int = 0,
    symbols_found: int = 0,
    relations_built: int = 0,
    duration_ms: int = 0,
    incremental: bool = False,
    agent: str = "code-indexer",
) -> str | None:
    """Emit code graph index event."""
    return emit("code_index", agent=agent, project=project, data={
        "files_indexed": files_indexed,
        "symbols_found": symbols_found,
        "relations_built": relations_built,
        "duration_ms": duration_ms,
        "incremental": incremental,
    })


def emit_code_impact(
    project: str,
    symbol: str,
    depth_1: int = 0,
    depth_2: int = 0,
    depth_3: int = 0,
    risk: str = "LOW",
    agent: str = "code-indexer",
) -> str | None:
    """Emit code impact analysis event."""
    return emit("code_impact", agent=agent, project=project, data={
        "symbol": symbol,
        "depth_1": depth_1,
        "depth_2": depth_2,
        "depth_3": depth_3,
        "risk": risk,
    })


def emit_code_trace(
    project: str,
    entry_point: str,
    depth: int = 0,
    cycle_detected: bool = False,
    agent: str = "code-indexer",
) -> str | None:
    """Emit code trace event."""
    return emit("code_trace", agent=agent, project=project, data={
        "entry_point": entry_point,
        "depth": depth,
        "cycle_detected": cycle_detected,
    })


# ── Query helpers ────────────────────────────────────────────────────────

def read_trace(session_id: str, limit: int = 100) -> list[dict]:
    """Read events from a trace file."""
    trace_path = TRACES_DIR / f"{session_id}.jsonl"
    if not trace_path.exists():
        return []

    events = []
    try:
        with open(trace_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
                if limit and len(events) >= limit:
                    break
    except Exception:
        pass

    return events


def read_recent_events(
    project: str = "",
    event: str = "",
    limit: int = 50,
) -> list[dict]:
    """Read recent events across all sessions, optionally filtered."""
    if not TRACES_DIR.exists():
        return []

    all_events = []
    for trace_file in sorted(TRACES_DIR.glob("*.jsonl"), reverse=True):
        try:
            with open(trace_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if project and rec.get("project") != project:
                        continue
                    if event and rec.get("event") != event:
                        continue
                    all_events.append(rec)
                    if len(all_events) >= limit:
                        return all_events
        except Exception:
            continue

    return all_events


def get_last_event_time(project: str = "") -> str | None:
    """Get timestamp of most recent event for a project."""
    events = read_recent_events(project=project, limit=1)
    if events:
        return events[0].get("ts")
    return None


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    """CLI interface for trace operations."""
    import argparse

    parser = argparse.ArgumentParser(description="EDMS Trace Emitter")
    sub = parser.add_subparsers(dest="cmd")

    p_emit = sub.add_parser("emit", help="Emit a test event")
    p_emit.add_argument("event", help="Event name")
    p_emit.add_argument("--project", default="test", help="Project name")
    p_emit.add_argument("--agent", default="cli", help="Agent name")
    p_emit.add_argument("--data", default="{}", help="JSON data")

    p_read = sub.add_parser("read", help="Read trace events")
    p_read.add_argument("--session", default=None, help="Session ID")
    p_read.add_argument("--project", default="", help="Filter by project")
    p_read.add_argument("--event", default="", help="Filter by event type")
    p_read.add_argument("--limit", type=int, default=20, help="Max events")

    p_last = sub.add_parser("last", help="Show last event time")
    p_last.add_argument("--project", default="", help="Project name")

    p_status = sub.add_parser("status", help="Show trace status")

    args = parser.parse_args()

    if args.cmd == "emit":
        data = json.loads(args.data)
        path = emit(args.event, project=args.project, agent=args.agent, data=data)
        print(f"Emitted to: {path}")

    elif args.cmd == "read":
        if args.session:
            events = read_trace(args.session, limit=args.limit)
        else:
            events = read_recent_events(project=args.project, event=args.event, limit=args.limit)
        for e in events:
            print(json.dumps(e, ensure_ascii=False))

    elif args.cmd == "last":
        ts = get_last_event_time(args.project)
        if ts:
            print(f"Last event: {ts}")
        else:
            print("No events found")

    elif args.cmd == "status":
        if not TRACES_DIR.exists():
            print("No traces directory")
            return
        files = list(TRACES_DIR.glob("*.jsonl"))
        total_size = sum(f.stat().st_size for f in files)
        print(f"Sessions: {len(files)}")
        print(f"Total size: {total_size / 1024:.1f} KB")
        index_path = TRACES_DIR / "index.json"
        if index_path.exists():
            index = json.loads(index_path.read_text())
            print(f"Indexed sessions: {len(index)}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
