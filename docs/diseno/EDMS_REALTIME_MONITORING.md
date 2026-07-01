# EDMS Real-Time Monitoring — Architecture Design

**Status:** DRAFT  
**Date:** 2026-06-06  
**Depends on:** NFR-008 (Traces NDJSON), EDMS UI Stack, Wireframes  

---

## 1. Executive Summary

Design a real-time monitoring system for EDMS that provides:
1. Live graph updates when files are created/modified
2. Project state machine (Active → Paused after 10min inactivity)
3. Agent loop detection (repeating actions = token overconsumption)
4. Dashboard visual consuming events via SSE (Server-Sent Events)

**Key constraint:** Minimal invasiveness — leverage existing hooks and NDJSON pattern.

---

## 2. Event Emission Layer

### 2.1 Event Types

```python
# scripts/evol_traces.py — Event Schema

@dataclass
class TraceEvent:
    timestamp: str          # ISO 8601
    event: str              # Event type (see catalog)
    session_id: str         # From EVOL_SESSION_ID or generated
    agent: str              # Agent name or "hook:*"
    project: str            # Project path
    data: dict              # Event-specific payload

EVENT_CATALOG = {
    # Graph events
    "graph.node.added":     {"node_id": str, "node_type": str, "properties": dict},
    "graph.relation.added": {"source": str, "target": str, "relation": str},
    "graph.node.updated":   {"node_id": str, "changes": dict},
    
    # File events (from hooks)
    "file.created":    {"path": str, "tipo": str, "sprint": str},
    "file.modified":   {"path": str, "tipo": str, "content_hash": str},
    "file.indexed":    {"path": str, "doc_id": str, "engine": str},
    
    # Session events
    "session.start":   {"agent": str, "branch": str},
    "session.end":     {"duration_sec": int, "messages": int},
    
    # State machine events
    "state.transition": {"from": str, "to": str, "trigger": str, "project": str},
    
    # Agent events
    "agent.action":    {"agent": str, "action": str, "tool": str, "target": str},
    "agent.loop.detected": {"agent": str, "repetition_count": int, "pattern": str},
    
    # Pipeline events
    "phase.enter":     {"phase": str, "sprint": str},
    "phase.exit":      {"phase": str, "sprint": str, "artifacts": list},
    "gate.approved":   {"gate_id": str, "phase": str},
}
```

### 2.2 Emission Points

| Location | File | Event | Trigger |
|----------|------|-------|---------|
| Hook: post-edit | `.agent/hooks/scripts/post-edit-memory-index.sh` | `file.created/modified/indexed` | After successful EDMS index |
| MemoryStore.index | `scripts/evol_memory_store.py:242` | `graph.node.added`, `graph.relation.added` | After ChromaDB/stdlib upsert |
| MemoryStore.graph_add_node | `scripts/evol_memory_store.py:497` | `graph.node.added` | After node creation |
| MemoryStore.graph_add_relation | `scripts/evol_memory_store.py:521` | `graph.relation.added` | After relation creation |
| evol-gate.py | `scripts/evol-gate.py:213` | `gate.approved` | After HMAC approval |
| session-start hook | `.agent/hooks/scripts/session-start-context-load.sh` | `session.start` | Session begin |
| session-end hook | `.agent/hooks/scripts/session-end-handoff.sh` | `session.end` | Session end |

### 2.3 Emission Implementation

```python
# scripts/evol_traces.py — Minimal Trace Emitter

import json, os, sys
from datetime import datetime
from pathlib import Path

TRACES_DIR = Path(os.environ.get("EVOL_TRACES_DIR", ".evol/traces"))
_session_id = None

def _ensure_dir():
    TRACES_DIR.mkdir(parents=True, exist_ok=True)

def _get_session_id():
    global _session_id
    if _session_id is None:
        _session_id = os.environ.get("EVOL_SESSION_ID", 
            datetime.now().strftime("%Y%m%d-%H%M%S"))
    return _session_id

def emit(event: str, data: dict, agent: str = "system", project: str = "."):
    """Emit a trace event to NDJSON file. Zero-dependency, stdlib only."""
    _ensure_dir()
    trace = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "session_id": _get_session_id(),
        "agent": agent,
        "project": project,
        "data": data,
    }
    trace_file = TRACES_DIR / f"{_get_session_id()}.jsonl"
    with open(trace_file, "a") as f:
        f.write(json.dumps(trace, ensure_ascii=False) + "\n")
    return trace

def emit_graph_add(node_type: str, properties: dict, project: str = "."):
    """Convenience: emit graph.node.added event."""
    node_id = properties.get("name", "unknown")
    return emit("graph.node.added", {
        "node_id": node_id,
        "node_type": node_type,
        "properties": properties,
    }, project=project)

def emit_graph_relation(source: str, target: str, relation: str, project: str = "."):
    """Convenience: emit graph.relation.added event."""
    return emit("graph.relation.added", {
        "source": source,
        "target": target,
        "relation": relation,
    }, project=project)

def emit_file_event(event_type: str, path: str, **kwargs):
    """Convenience: emit file.* event."""
    return emit(event_type, {"path": path, **kwargs})
```

---

## 3. Event Storage

### 3.1 NDJSON Structure (NFR-008 Compliant)

Location: `.evol/traces/<session-id>.jsonl`

```jsonl
{"timestamp":"2026-06-06T10:00:00Z","event":"session.start","session_id":"20260606-100000","agent":"orchestrator","project":".","data":{"branch":"feature/edms-ui"}}
{"timestamp":"2026-06-06T10:00:05Z","event":"file.created","session_id":"20260606-100000","agent":"hook:post-edit","project":".","data":{"path":"acuerdos/memoria/decisiones.md","tipo":"decision","sprint":"27"}}
{"timestamp":"2026-06-06T10:00:06Z","event":"graph.node.added","session_id":"20260606-100000","agent":"evol-memory","project":".","data":{"node_id":"decision-abc123","node_type":"Decision","properties":{"text":"Decidimos usar SSE","fecha":"2026-06-06"}}}
{"timestamp":"2026-06-06T10:00:06Z","event":"graph.relation.added","session_id":"20260606-100000","agent":"evol-memory","project":".","data":{"source":"evol-dd","target":"decision-abc123","relation":"Genera"}}
{"timestamp":"2026-06-06T10:10:00Z","event":"state.transition","session_id":"20260606-100000","agent":"system","project":".","data":{"from":"active","to":"paused","trigger":"inactivity_10min"}}
{"timestamp":"2026-06-06T10:15:00Z","event":"agent.loop.detected","session_id":"20260606-100000","agent":"system","project":".","data":{"agent":"evol-builder","repetition_count":5,"pattern":"edit→index→edit→index"}}
```

### 3.2 File Rotation

```python
# scripts/evol_traces.py — File Management

MAX_FILE_SIZE_MB = 10  # Rotate after 10MB
MAX_FILES = 50         # Keep last 50 session files

def _rotate_if_needed():
    """Rotate trace file if too large."""
    trace_file = TRACES_DIR / f"{_get_session_id()}.jsonl"
    if trace_file.exists() and trace_file.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        rotated = trace_file.with_suffix(f".{datetime.now().strftime('%H%M%S')}.jsonl")
        trace_file.rename(rotated)
        # Cleanup old files
        files = sorted(TRACES_DIR.glob("*.jsonl"), key=lambda f: f.stat().st_mtime)
        for old_file in files[:-MAX_FILES]:
            old_file.unlink()
```

### 3.3 Index File (Fast Access)

```python
# .evol/traces/index.json — Session Registry

{
  "sessions": [
    {
      "id": "20260606-100000",
      "file": "20260606-100000.jsonl",
      "project": ".",
      "started_at": "2026-06-06T10:00:00Z",
      "events_count": 47,
      "size_bytes": 12340
    }
  ],
  "last_updated": "2026-06-06T10:15:00Z"
}
```

---

## 4. Event Processing

### 4.1 Project State Machine

```
                    ┌─────────────┐
                    │   CREATED   │
                    └──────┬──────┘
                           │ first activity
                           ▼
                    ┌─────────────┐
         ┌─────────│    ACTIVE   │─────────┐
         │         └──────┬──────┘         │
         │                │                │
    user activity    10min silence    user activity
         │                │                │
         ▼                ▼                │
┌─────────────┐   ┌─────────────┐         │
│   ACTIVE    │   │   PAUSED    │─────────┘
└─────────────┘   └──────┬──────┘
                         │ resume
                         ▼
                  ┌─────────────┐
                  │   ACTIVE    │
                  └─────────────┘
```

```python
# scripts/evol_state_machine.py — Project State Machine

import json, os, time
from datetime import datetime, timedelta
from pathlib import Path
from _evol_common import get_logger

logger = get_logger("state_machine")

STATE_FILE = Path(".evol/project-state.json")
INACTIVITY_TIMEOUT = timedelta(minutes=10)

STATES = ["created", "active", "paused", "archived"]

def get_state(project: str = ".") -> dict:
    """Get current project state."""
    state_file = STATE_FILE
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return {
        "project": project,
        "state": "created",
        "last_activity": datetime.utcnow().isoformat() + "Z",
        "transitions": [],
    }

def update_activity(project: str = "."):
    """Record activity and handle state transitions."""
    state = get_state(project)
    now = datetime.utcnow()
    last_activity = datetime.fromisoformat(state["last_activity"].replace("Z", ""))
    
    old_state = state["state"]
    
    # If paused, transition to active on any activity
    if old_state == "paused":
        state["state"] = "active"
        state["transitions"].append({
            "from": "paused",
            "to": "active",
            "trigger": "user_activity",
            "timestamp": now.isoformat() + "Z",
        })
        _emit_state_transition(project, "paused", "active", "user_activity")
    
    # If created, transition to active on first activity
    elif old_state == "created":
        state["state"] = "active"
        state["transitions"].append({
            "from": "created",
            "to": "active",
            "trigger": "first_activity",
            "timestamp": now.isoformat() + "Z",
        })
        _emit_state_transition(project, "created", "active", "first_activity")
    
    state["last_activity"] = now.isoformat() + "Z"
    _save_state(state)
    return state

def check_inactivity():
    """Check for projects that should transition to paused."""
    state = get_state()
    if state["state"] != "active":
        return state
    
    now = datetime.utcnow()
    last_activity = datetime.fromisoformat(state["last_activity"].replace("Z", ""))
    
    if now - last_activity > INACTIVITY_TIMEOUT:
        old_state = state["state"]
        state["state"] = "paused"
        state["transitions"].append({
            "from": old_state,
            "to": "paused",
            "trigger": "inactivity_10min",
            "timestamp": now.isoformat() + "Z",
        })
        _save_state(state)
        _emit_state_transition(state["project"], old_state, "paused", "inactivity_10min")
    
    return state

def _save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def _emit_state_transition(project: str, from_state: str, to_state: str, trigger: str):
    """Emit state transition event."""
    try:
        from evol_traces import emit
        emit("state.transition", {
            "from": from_state,
            "to": to_state,
            "trigger": trigger,
            "project": project,
        })
    except ImportError:
        pass  # Traces not available
```

### 4.2 Agent Loop Detection

```python
# scripts/evol_loop_detector.py — Agent Loop Detection

import json, os, time
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from _evol_common import get_logger

logger = get_logger("loop_detector")

# Sliding window: last N actions per agent
WINDOW_SIZE = 20
LOOP_THRESHOLD = 3  # Same pattern repeated 3+ times
ACTION_HISTORY = {}  # agent -> deque of (action_hash, timestamp)

def _action_hash(action: dict) -> str:
    """Create a hashable fingerprint of an action."""
    # Normalize: ignore timestamps, focus on semantic content
    key_parts = [
        action.get("tool", ""),
        action.get("target", ""),
        action.get("action_type", ""),
    ]
    return "|".join(key_parts)

def record_action(agent: str, action: dict):
    """Record an agent action and check for loops."""
    if agent not in ACTION_HISTORY:
        ACTION_HISTORY[agent] = deque(maxlen=WINDOW_SIZE)
    
    hash_val = _action_hash(action)
    now = time.time()
    
    ACTION_HISTORY[agent].append({
        "hash": hash_val,
        "timestamp": now,
        "action": action,
    })
    
    return check_loop(agent)

def check_loop(agent: str) -> dict | None:
    """Check if agent is in a loop. Returns loop info or None."""
    if agent not in ACTION_HISTORY:
        return None
    
    history = ACTION_HISTORY[agent]
    if len(history) < LOOP_THRESHOLD:
        return None
    
    # Check for repeated pattern in last N actions
    recent_hashes = [h["hash"] for h in list(history)[-WINDOW_SIZE:]]
    
    # Count consecutive repetitions
    max_repeat = 1
    current_repeat = 1
    pattern = None
    
    for i in range(1, len(recent_hashes)):
        if recent_hashes[i] == recent_hashes[i-1]:
            current_repeat += 1
            if current_repeat > max_repeat:
                max_repeat = current_repeat
                pattern = recent_hashes[i]
        else:
            current_repeat = 1
    
    # Also check for alternating pattern (A-B-A-B-A-B)
    if len(recent_hashes) >= 4:
        for window in [2, 3]:
            if len(recent_hashes) >= window * 2:
                pat = recent_hashes[:window]
                matches = sum(
                    1 for i in range(window, len(recent_hashes))
                    if recent_hashes[i] == pat[i % window]
                )
                if matches >= LOOP_THRESHOLD:
                    max_repeat = matches
                    pattern = "-".join(pat)
    
    if max_repeat >= LOOP_THRESHOLD:
        loop_info = {
            "agent": agent,
            "repetition_count": max_repeat,
            "pattern": pattern,
            "window_size": len(recent_hashes),
            "detected_at": datetime.utcnow().isoformat() + "Z",
            "token_risk": _estimate_token_risk(max_repeat),
        }
        _emit_loop_detected(loop_info)
        logger.warning(f"Loop detected for {agent}: {pattern} repeated {max_repeat} times")
        return loop_info
    
    return None

def _estimate_token_risk(repetition_count: int) -> str:
    """Estimate token overconsumption risk."""
    if repetition_count >= 10:
        return "CRITICAL"
    elif repetition_count >= 5:
        return "HIGH"
    elif repetition_count >= 3:
        return "MEDIUM"
    return "LOW"

def _emit_loop_detected(loop_info: dict):
    """Emit loop detection event."""
    try:
        from evol_traces import emit
        emit("agent.loop.detected", loop_info)
    except ImportError:
        pass

def reset_agent(agent: str):
    """Reset history for an agent (e.g., on phase change)."""
    ACTION_HISTORY.pop(agent, None)
```

### 4.3 Live Graph Updater

```python
# scripts/evol_graph_live.py — Live Graph Update Processor

import json, os
from pathlib import Path
from datetime import datetime
from _evol_common import get_logger

logger = get_logger("graph_live")

class GraphEventProcessor:
    """Process graph events and maintain live state for UI consumption."""
    
    def __init__(self, project: str = "."):
        self.project = project
        self.state_file = Path(".evol/graph-live.json")
        self._load_state()
    
    def _load_state(self):
        """Load or initialize live graph state."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                "nodes": [],
                "relations": [],
                "last_updated": None,
                "version": 0,
            }
    
    def process_event(self, event: dict):
        """Process a single graph event and update live state."""
        event_type = event.get("event", "")
        data = event.get("data", {})
        
        if event_type == "graph.node.added":
            self._add_node(data)
        elif event_type == "graph.relation.added":
            self._add_relation(data)
        elif event_type == "graph.node.updated":
            self._update_node(data)
        
        self.state["last_updated"] = datetime.utcnow().isoformat() + "Z"
        self.state["version"] += 1
        self._save_state()
    
    def _add_node(self, data: dict):
        node_id = data.get("node_id", "unknown")
        # Check if node exists
        existing = next((n for n in self.state["nodes"] if n["id"] == node_id), None)
        if existing:
            existing.update(data.get("properties", {}))
        else:
            self.state["nodes"].append({
                "id": node_id,
                "type": data.get("node_type", "unknown"),
                **data.get("properties", {}),
            })
    
    def _add_relation(self, data: dict):
        # Check if relation exists
        exists = any(
            r["source"] == data.get("source") and r["target"] == data.get("target")
            for r in self.state["relations"]
        )
        if not exists:
            self.state["relations"].append({
                "source": data.get("source"),
                "target": data.get("target"),
                "type": data.get("relation"),
            })
    
    def _update_node(self, data: dict):
        node_id = data.get("node_id", "unknown")
        for node in self.state["nodes"]:
            if node["id"] == node_id:
                node.update(data.get("changes", {}))
                break
    
    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def get_snapshot(self) -> dict:
        """Get current graph state for UI consumption."""
        return {
            "nodes": self.state["nodes"],
            "relations": self.state["relations"],
            "version": self.state["version"],
            "last_updated": self.state["last_updated"],
        }
```

---

## 5. Event Delivery

### 5.1 SSE Server (FastAPI)

```python
# scripts/evol_sse_server.py — SSE Event Server

import asyncio, json, os
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

# FastAPI + SSE
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EDMS Monitor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory event queue for SSE
event_queue: asyncio.Queue = asyncio.Queue()

# ── SSE Endpoint ──────────────────────────────────────────────────────────────

async def event_generator() -> AsyncGenerator[str, None]:
    """Generate SSE events from the queue."""
    while True:
        try:
            event = await asyncio.wait_for(event_queue.get(), timeout=30)
            yield f"data: {json.dumps(event)}\n\n"
        except asyncio.TimeoutError:
            # Send keepalive
            yield f": keepalive {datetime.utcnow().isoformat()}\n\n"

@app.get("/api/v1/events")
async def sse_events(request: Request):
    """SSE endpoint for real-time events."""
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

# ── REST Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/v1/edms/graph/live")
async def get_live_graph():
    """Get current live graph state."""
    from evol_graph_live import GraphEventProcessor
    processor = GraphEventProcessor()
    return processor.get_snapshot()

@app.get("/api/v1/edms/state")
async def get_project_state():
    """Get current project state."""
    from evol_state_machine import get_state
    return get_state()

@app.get("/api/v1/edms/loops")
async def get_active_loops():
    """Get current loop detection status."""
    from evol_loop_detector import ACTION_HISTORY
    loops = {}
    for agent, history in ACTION_HISTORY.items():
        from evol_loop_detector import check_loop
        loop = check_loop(agent)
        if loop:
            loops[agent] = loop
    return loops

@app.get("/api/v1/traces/{session_id}")
async def get_trace(session_id: str):
    """Get trace file for a session."""
    trace_file = Path(f".evol/traces/{session_id}.jsonl")
    if not trace_file.exists():
        return {"error": "Session not found"}
    events = []
    with open(trace_file) as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return {"session_id": session_id, "events": events}

# ── Event Processing ──────────────────────────────────────────────────────────

async def process_trace_file(trace_file: Path):
    """Watch and process a trace file for SSE broadcasting."""
    from evol_graph_live import GraphEventProcessor
    from evol_state_machine import update_activity
    from evol_loop_detector import record_action
    
    processor = GraphEventProcessor()
    
    with open(trace_file) as f:
        # Seek to end, then watch for new lines
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.5)
                continue
            
            try:
                event = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            
            # Broadcast via SSE
            await event_queue.put(event)
            
            # Process graph events
            if event.get("event", "").startswith("graph."):
                processor.process_event(event)
            
            # Update state machine
            if event.get("event", "").startswith("file.") or event.get("event", "").startswith("agent."):
                update_activity()
            
            # Record agent actions for loop detection
            if event.get("event", "") == "agent.action":
                agent = event.get("agent", "unknown")
                record_action(agent, event.get("data", {}))
```

### 5.2 File Watcher (Alternative to SSE)

```python
# scripts/evol_trace_watcher.py — File-based Event Watcher

import os, json, time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TraceWatcher(FileSystemEventHandler):
    """Watch .evol/traces/ for new events and process them."""
    
    def __init__(self, callback):
        self.callback = callback
        self._processed = set()
    
    def on_modified(self, event):
        if event.src_path.endswith(".jsonl"):
            self._process_file(event.src_path)
    
    def _process_file(self, filepath: str):
        with open(filepath) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    event = json.loads(line.strip())
                    event_key = f"{event.get('timestamp')}:{event.get('event')}"
                    if event_key not in self._processed:
                        self._processed.add(event_key)
                        self.callback(event)
                except json.JSONDecodeError:
                    continue

def start_watching(callback):
    """Start watching .evol/traces/ for changes."""
    traces_dir = Path(".evol/traces")
    traces_dir.mkdir(parents=True, exist_ok=True)
    
    observer = Observer()
    observer.schedule(TraceWatcher(callback), str(traces_dir), recursive=False)
    observer.start()
    return observer
```

---

## 6. UI Consumption

### 6.1 React Event Hook

```typescript
// src/hooks/useEDMSEvents.ts — React SSE Hook

import { useEffect, useState, useCallback } from 'react';

interface TraceEvent {
  timestamp: string;
  event: string;
  session_id: string;
  agent: string;
  data: Record<string, unknown>;
}

interface UseEDMSEventsOptions {
  url?: string;
  onEvent?: (event: TraceEvent) => void;
  onGraphUpdate?: (event: TraceEvent) => void;
  onStateChange?: (event: TraceEvent) => void;
  onLoopDetected?: (event: TraceEvent) => void;
}

export function useEDMSEvents(options: UseEDMSEventsOptions = {}) {
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const url = options.url || 'http://localhost:8000/api/v1/events';
  
  useEffect(() => {
    const eventSource = new EventSource(url);
    
    eventSource.onopen = () => setConnected(true);
    eventSource.onerror = () => {
      setConnected(false);
      setError('Connection lost');
    };
    
    eventSource.onmessage = (e) => {
      try {
        const event: TraceEvent = JSON.parse(e.data);
        setEvents(prev => [...prev.slice(-100), event]); // Keep last 100
        options.onEvent?.(event);
        
        // Route to specific handlers
        if (event.event.startsWith('graph.')) {
          options.onGraphUpdate?.(event);
        } else if (event.event === 'state.transition') {
          options.onStateChange?.(event);
        } else if (event.event === 'agent.loop.detected') {
          options.onLoopDetected?.(event);
        }
      } catch (err) {
        console.error('Failed to parse event:', err);
      }
    };
    
    return () => eventSource.close();
  }, [url]);
  
  return { events, connected, error };
}
```

### 6.2 Live Graph Component

```typescript
// src/components/LiveGraph.tsx — Real-time Knowledge Graph

import { useEffect, useRef } from 'react';
import { useEDMSEvents } from '../hooks/useEDMSEvents';

interface GraphNode {
  id: string;
  type: string;
  x?: number;
  y?: number;
  label?: string;
}

interface GraphRelation {
  source: string;
  target: string;
  type: string;
}

export function LiveGraph() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<Map<string, GraphNode>>(new Map());
  const relationsRef = useRef<GraphRelation[]>([]);
  
  const { events, connected } = useEDMSEvents({
    onGraphUpdate: (event) => {
      if (event.event === 'graph.node.added') {
        const { node_id, node_type, properties } = event.data;
        nodesRef.current.set(node_id, {
          id: node_id,
          type: node_type,
          label: properties?.name || node_id,
          x: Math.random() * 800,
          y: Math.random() * 600,
        });
        renderGraph();
      } else if (event.event === 'graph.relation.added') {
        relationsRef.current.push({
          source: event.data.source,
          target: event.data.target,
          type: event.data.relation,
        });
        renderGraph();
      }
    },
  });
  
  const renderGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw relations
    ctx.strokeStyle = '#4F46E5';
    ctx.lineWidth = 1;
    for (const rel of relationsRef.current) {
      const source = nodesRef.current.get(rel.source);
      const target = nodesRef.current.get(rel.target);
      if (source?.x && source.y && target?.x && target.y) {
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();
      }
    }
    
    // Draw nodes
    for (const node of nodesRef.current.values()) {
      if (!node.x || !node.y) continue;
      
      ctx.fillStyle = getNodeColor(node.type);
      ctx.beginPath();
      ctx.arc(node.x, node.y, 8, 0, Math.PI * 2);
      ctx.fill();
      
      ctx.fillStyle = '#FFFFFF';
      ctx.font = '12px Inter';
      ctx.textAlign = 'center';
      ctx.fillText(node.label || node.id, node.x, node.y + 20);
    }
  };
  
  const getNodeColor = (type: string): string => {
    const colors: Record<string, string> = {
      'Decision': '#4F46E5',
      'Leccion': '#10B981',
      'Artefacto': '#F59E0B',
      'Disciplina': '#8B5CF6',
      'Proyecto': '#EF4444',
      'Sprint': '#06B6D4',
    };
    return colors[type] || '#6B7280';
  };
  
  return (
    <div className="relative">
      <div className="absolute top-2 right-2 flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-xs text-gray-500">{connected ? 'Live' : 'Disconnected'}</span>
      </div>
      <canvas
        ref={canvasRef}
        width={800}
        height={600}
        className="border border-gray-200 rounded-lg"
      />
    </div>
  );
}
```

### 6.3 State Machine Indicator

```typescript
// src/components/ProjectStateIndicator.tsx

import { useEffect, useState } from 'react';
import { useEDMSEvents } from '../hooks/useEDMSEvents';

type ProjectState = 'created' | 'active' | 'paused' | 'archived';

export function ProjectStateIndicator() {
  const [state, setState] = useState<ProjectState>('created');
  const [lastTransition, setLastTransition] = useState<string>('');
  
  const { events } = useEDMSEvents({
    onStateChange: (event) => {
      if (event.event === 'state.transition') {
        setState(event.data.to as ProjectState);
        setLastTransition(
          `${event.data.from} → ${event.data.to} (${event.data.trigger})`
        );
      }
    },
  });
  
  const stateConfig: Record<ProjectState, { color: string; label: string }> = {
    created: { color: 'bg-gray-400', label: 'Created' },
    active: { color: 'bg-green-500', label: 'Active' },
    paused: { color: 'bg-yellow-500', label: 'Paused (10min silence)' },
    archived: { color: 'bg-blue-500', label: 'Archived' },
  };
  
  const config = stateConfig[state];
  
  return (
    <div className="flex items-center gap-2">
      <span className={`w-3 h-3 rounded-full ${config.color}`} />
      <span className="font-medium">{config.label}</span>
      {lastTransition && (
        <span className="text-xs text-gray-500 ml-2">
          Last: {lastTransition}
        </span>
      )}
    </div>
  );
}
```

---

## 7. Phased Implementation

### Phase 1: Foundation (Week 1)

**Goal:** Event emission + NDJSON storage + basic SSE

| Task | File | Effort |
|------|------|--------|
| Create `evol_traces.py` | `scripts/evol_traces.py` | Low |
| Add `emit()` calls to `evol_memory_store.py` | `scripts/evol_memory_store.py` | Low |
| Add `emit()` calls to `post-edit-memory-index.sh` | `.agent/hooks/scripts/post-edit-memory-index.sh` | Low |
| Create `.evol/traces/` directory | Auto-created by `evol_traces.py` | - |
| Create basic SSE server | `scripts/evol_sse_server.py` | Medium |
| Update NFR-008 status to IMPLEMENTED | `docs/requisitos/NO_FUNCIONALES.md` | - |

**Deliverable:** Events emitted on graph changes, stored in NDJSON, queryable via REST.

### Phase 2: Processing (Week 2)

**Goal:** State machine + loop detection + live graph

| Task | File | Effort |
|------|------|--------|
| Create `evol_state_machine.py` | `scripts/evol_state_machine.py` | Medium |
| Create `evol_loop_detector.py` | `scripts/evol_loop_detector.py` | Medium |
| Create `evol_graph_live.py` | `scripts/evol_graph_live.py` | Medium |
| Integrate state machine with `post-edit-memory-index.sh` | `.agent/hooks/scripts/post-edit-memory-index.sh` | Low |
| Add 10-min inactivity cron | `.agent/hooks/hooks.json` | Low |

**Deliverable:** Project auto-pauses after 10min, loops detected, live graph maintained.

### Phase 3: UI (Week 3)

**Goal:** React dashboard integration

| Task | File | Effort |
|------|------|--------|
| Create `useEDMSEvents` hook | `src/hooks/useEDMSEvents.ts` | Medium |
| Create `LiveGraph` component | `src/components/LiveGraph.tsx` | High |
| Create `ProjectStateIndicator` component | `src/components/ProjectStateIndicator.tsx` | Low |
| Create `LoopAlert` component | `src/components/LoopAlert.tsx` | Low |
| Integrate with existing wireframes | `acuerdos/design/wireframes/propuesta/` | Medium |

**Deliverable:** Real-time dashboard with live graph, state indicator, loop alerts.

---

## 8. File Inventory

### New Files

| File | Purpose |
|------|---------|
| `scripts/evol_traces.py` | Event emission + NDJSON storage |
| `scripts/evol_state_machine.py` | Project state machine (Active → Paused) |
| `scripts/evol_loop_detector.py` | Agent loop detection |
| `scripts/evol_graph_live.py` | Live graph state processor |
| `scripts/evol_sse_server.py` | SSE event server (FastAPI) |
| `scripts/evol_trace_watcher.py` | File-based event watcher (alternative to SSE) |
| `.evol/traces/` | NDJSON trace files directory |
| `.evol/graph-live.json` | Live graph state |
| `.evol/project-state.json` | Project state machine state |
| `src/hooks/useEDMSEvents.ts` | React SSE hook |
| `src/components/LiveGraph.tsx` | Live graph component |
| `src/components/ProjectStateIndicator.tsx` | State indicator |
| `src/components/LoopAlert.tsx` | Loop detection alert |

### Modified Files

| File | Change |
|------|--------|
| `scripts/evol_memory_store.py` | Add `emit()` calls in `index()`, `graph_add_node()`, `graph_add_relation()` |
| `.agent/hooks/scripts/post-edit-memory-index.sh` | Add trace emission after successful index |
| `.agent/hooks/hooks.json` | Add `pre:tool:agent-action` hook for loop detection |
| `_evol_common.py` | Add `get_traces_dir()` helper |
| `docs/requisitos/NO_FUNCIONALES.md` | Update NFR-008 status |

---

## 9. Invariants

- **Zero external dependencies** — stdlib Python only for traces/state/loops
- **NDJSON append-only** — never modify existing trace lines
- **Gitignored traces** — `.evol/traces/` in `.gitignore`
- **Token efficiency** — trace emission is fire-and-forget, no blocking
- **Fallback graceful** — if SSE unavailable, REST polling works
- **No MCP** — traces are local files, not MCP servers

---

## 10. Open Questions

1. **SSE vs WebSocket:** SSE chosen for simplicity (one-way, auto-reconnect). WebSocket if bidirectional needed later.
2. **Graph layout:** Canvas with force-directed layout. Consider react-force-graph if complexity grows.
3. **Loop detection tuning:** Threshold=3 may need adjustment per agent type.
4. **State machine persistence:** JSON file sufficient for single-project. SQLite if multi-project.
5. **Wireframe integration:** Existing wireframes need update to show live indicators.
