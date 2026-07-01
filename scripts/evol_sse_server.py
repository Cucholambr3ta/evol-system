#!/usr/bin/env python3
"""EDMS Real-Time SSE Server — stdlib-only.

Streams NDJSON trace events to connected clients via Server-Sent Events.
No external dependencies (uses http.server + threading).

Usage:
  python3 evol_sse_server.py [--port 8765] [--host 0.0.0.0]

Endpoints:
  GET /api/v1/events          — SSE stream of all events
  GET /api/v1/events?project=X — SSE stream filtered by project
  GET /api/v1/state           — Current project state (Active/Paused/Error)
  GET /api/v1/loops           — Detected agent loops
  GET /api/v1/status          — Server status
  GET /                       — Simple dashboard HTML
"""

import json
import os
import sys
import time
import threading
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import Any

# ── Config ────────────────────────────────────────────────────────────────

TRACES_DIR = Path(os.environ.get("EVOL_TRACES_DIR", ".evol/traces"))
DEFAULT_PORT = int(os.environ.get("EVOL_SSE_PORT", "8765"))
DEFAULT_HOST = os.environ.get("EVOL_SSE_HOST", "0.0.0.0")
POLL_INTERVAL = 1.0  # seconds between file checks

# ── State Machine ────────────────────────────────────────────────────────

class ProjectStateMachine:
    """Track project state: Active → Paused → Error."""

    PAUSE_THRESHOLD = 600  # 10 minutes

    def __init__(self):
        self._states: dict[str, dict] = {}
        self._lock = threading.Lock()

    def update(self, project: str, event: dict) -> str:
        """Update state based on new event. Returns current state."""
        with self._lock:
            now = time.time()
            if project not in self._states:
                self._states[project] = {
                    "state": "active",
                    "last_event_ts": now,
                    "last_event": event,
                    "event_count": 0,
                    "error_count": 0,
                }

            ps = self._states[project]
            ps["last_event_ts"] = now
            ps["last_event"] = event
            ps["event_count"] += 1

            if event.get("event") == "error":
                ps["error_count"] += 1
                if ps["error_count"] >= 3:
                    ps["state"] = "error"
            else:
                ps["error_count"] = 0
                ps["state"] = "active"

            return ps["state"]

    def check_paused(self) -> dict[str, str]:
        """Check if any projects should be paused. Returns changed states."""
        with self._lock:
            now = time.time()
            changed = {}
            for project, ps in self._states.items():
                if ps["state"] == "active":
                    if now - ps["last_event_ts"] > self.PAUSE_THRESHOLD:
                        ps["state"] = "paused"
                        changed[project] = "paused"
                elif ps["state"] == "paused":
                    if now - ps["last_event_ts"] <= self.PAUSE_THRESHOLD:
                        ps["state"] = "active"
                        changed[project] = "active"
            return changed

    def get_state(self, project: str = "") -> dict:
        """Get current state for a project or all projects."""
        with self._lock:
            if project:
                ps = self._states.get(project)
                if ps:
                    return {
                        "project": project,
                        "state": ps["state"],
                        "last_event_ts": datetime.fromtimestamp(ps["last_event_ts"], tz=timezone.utc).isoformat(),
                        "event_count": ps["event_count"],
                        "error_count": ps["error_count"],
                    }
                return {"project": project, "state": "unknown"}
            return {
                p: {
                    "state": ps["state"],
                    "last_event_ts": datetime.fromtimestamp(ps["last_event_ts"], tz=timezone.utc).isoformat(),
                    "event_count": ps["event_count"],
                }
                for p, ps in self._states.items()
            }


# ── Loop Detector ────────────────────────────────────────────────────────

class LoopDetector:
    """Detect agent loops (repeated actions in short window)."""

    WINDOW = 300  # 5 minutes
    THRESHOLD = 3  # same action 3+ times

    def __init__(self):
        self._actions: dict[str, list[dict]] = {}
        self._alerts: list[dict] = []
        self._lock = threading.Lock()

    def record(self, agent: str, action: str, project: str = "") -> dict | None:
        """Record an agent action. Returns alert if loop detected."""
        if not agent:
            return None

        key = f"{agent}:{project}"
        now = time.time()

        with self._lock:
            if key not in self._actions:
                self._actions[key] = []

            self._actions[key].append({
                "action": action,
                "ts": now,
            })

            # Prune old actions outside window
            self._actions[key] = [
                a for a in self._actions[key]
                if now - a["ts"] < self.WINDOW
            ]

            # Check for loop
            action_counts: dict[str, int] = {}
            for a in self._actions[key]:
                action_counts[a["action"]] = action_counts.get(a["action"], 0) + 1

            for action_name, count in action_counts.items():
                if count >= self.THRESHOLD:
                    alert = {
                        "agent": agent,
                        "project": project,
                        "action": action_name,
                        "count": count,
                        "window": self.WINDOW,
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "severity": "warning" if count < 5 else "critical",
                    }
                    self._alerts.append(alert)
                    return alert

            return None

    def get_alerts(self, project: str = "", limit: int = 20) -> list[dict]:
        """Get recent loop alerts."""
        with self._lock:
            alerts = self._alerts
            if project:
                alerts = [a for a in alerts if a.get("project") == project]
            return alerts[-limit:]


# ── SSE Clients ──────────────────────────────────────────────────────────

class SSEManager:
    """Manage SSE client connections."""

    def __init__(self):
        self._clients: list[dict] = []
        self._lock = threading.Lock()

    def add_client(self, client_id: str, project_filter: str = "") -> dict:
        """Register a new SSE client."""
        with self._lock:
            client = {
                "id": client_id,
                "project": project_filter,
                "queue": [],
                "connected_at": time.time(),
            }
            self._clients.append(client)
            return client

    def remove_client(self, client_id: str):
        """Remove an SSE client."""
        with self._lock:
            self._clients = [c for c in self._clients if c["id"] != client_id]

    def broadcast(self, event: dict, project: str = ""):
        """Broadcast event to all matching clients."""
        with self._lock:
            for client in self._clients:
                if not client["project"] or client["project"] == project:
                    client["queue"].append(event)

    def get_events(self, client_id: str, timeout: float = 30.0) -> list[dict]:
        """Get pending events for a client (blocks up to timeout)."""
        client = None
        with self._lock:
            for c in self._clients:
                if c["id"] == client_id:
                    client = c
                    break

        if not client:
            return []

        # Wait for events
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                if client["queue"]:
                    events = client["queue"][:]
                    client["queue"] = []
                    return events
            time.sleep(0.1)

        return []


# ── Global state ─────────────────────────────────────────────────────────

state_machine = ProjectStateMachine()
loop_detector = LoopDetector()
sse_manager = SSEManager()


# ── Trace file reader ────────────────────────────────────────────────────

class TraceReader:
    """Read NDJSON trace files and detect new events."""

    def __init__(self):
        self._offsets: dict[str, int] = {}
        self._lock = threading.Lock()

    def read_new_events(self) -> list[dict]:
        """Read new events from all trace files since last read."""
        if not TRACES_DIR.exists():
            return []

        new_events = []
        with self._lock:
            for trace_file in TRACES_DIR.glob("*.jsonl"):
                session_id = trace_file.stem
                last_offset = self._offsets.get(session_id, 0)

                try:
                    file_size = trace_file.stat().st_size
                    if file_size <= last_offset:
                        continue

                    with open(trace_file, "r", encoding="utf-8") as f:
                        f.seek(last_offset)
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    event = json.loads(line)
                                    event["_session_id"] = session_id
                                    new_events.append(event)
                                except json.JSONDecodeError:
                                    continue
                        self._offsets[session_id] = f.tell()
                except Exception:
                    continue

        return new_events


trace_reader = TraceReader()


# ── HTTP Handler ─────────────────────────────────────────────────────────

class SSEHandler(BaseHTTPRequestHandler):
    """HTTP handler for SSE server."""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/api/v1/events":
            self._handle_sse(params)
        elif path == "/api/v1/state":
            self._handle_state(params)
        elif path == "/api/v1/loops":
            self._handle_loops(params)
        elif path == "/api/v1/status":
            self._handle_status()
        elif path == "/":
            self._handle_dashboard()
        else:
            self.send_error(404)

    def _handle_sse(self, params: dict):
        """Handle SSE event stream."""
        project = params.get("project", [""])[0]
        client_id = f"client-{time.time_ns()}"

        client = sse_manager.add_client(client_id, project)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        try:
            # Send initial state
            state = state_machine.get_state(project)
            self._send_sse_event("state", state)

            # Stream events
            while True:
                events = sse_manager.get_events(client_id, timeout=30.0)
                for event in events:
                    self._send_sse_event(event.get("event", "unknown"), event)

                # Send keepalive
                self._send_sse_event("keepalive", {"ts": time.time()})
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            sse_manager.remove_client(client_id)

    def _send_sse_event(self, event_type: str, data: dict):
        """Send a single SSE event."""
        try:
            self.wfile.write(f"event: {event_type}\n".encode())
            self.wfile.write(f"data: {json.dumps(data, ensure_ascii=False)}\n\n".encode())
            self.wfile.flush()
        except Exception:
            raise ConnectionResetError("Client disconnected")

    def _handle_state(self, params: dict):
        """Handle state query."""
        project = params.get("project", [""])[0]
        state = state_machine.get_state(project)
        self._send_json(state)

    def _handle_loops(self, params: dict):
        """Handle loop alerts query."""
        project = params.get("project", [""])[0]
        alerts = loop_detector.get_alerts(project)
        self._send_json({"alerts": alerts})

    def _handle_status(self):
        """Handle status query."""
        traces_dir = TRACES_DIR
        files = list(traces_dir.glob("*.jsonl")) if traces_dir.exists() else []
        total_size = sum(f.stat().st_size for f in files)

        self._send_json({
            "status": "running",
            "traces": {
                "sessions": len(files),
                "total_size_kb": round(total_size / 1024, 1),
            },
            "projects": state_machine.get_state(),
            "loop_alerts": len(loop_detector.get_alerts()),
        })

    def _handle_dashboard(self):
        """Serve simple dashboard HTML."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>EDMS Monitor</title>
    <style>
        body { font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 20px; }
        h1 { color: #58a6ff; }
        .state { padding: 10px; margin: 5px 0; border-radius: 4px; }
        .active { background: #1a4d2e; border-left: 3px solid #3fb950; }
        .paused { background: #4d3a1a; border-left: 3px solid #d29922; }
        .error { background: #4d1a1a; border-left: 3px solid #f85149; }
        .unknown { background: #1a1a4d; border-left: 3px solid #58a6ff; }
        .event { padding: 5px; margin: 2px 0; font-size: 12px; border-bottom: 1px solid #21262d; }
        .alert { background: #4d1a1a; padding: 10px; margin: 5px 0; border-radius: 4px; }
        #events { max-height: 400px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>EDMS Real-Time Monitor</h1>
    <div id="state">Connecting...</div>
    <h2>Events</h2>
    <div id="events"></div>
    <h2>Loop Alerts</h2>
    <div id="alerts"></div>
    <script>
        const events = document.getElementById('events');
        const stateDiv = document.getElementById('state');
        const alertsDiv = document.getElementById('alerts');

        const evtSource = new EventSource('/api/v1/events');

        evtSource.addEventListener('state', (e) => {
            const data = JSON.parse(e.data);
            stateDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        });

        evtSource.addEventListener('edms_index', (e) => addEvent('INDEX', e.data));
        evtSource.addEventListener('edms_search', (e) => addEvent('SEARCH', e.data));
        evtSource.addEventListener('graph_node_created', (e) => addEvent('GRAPH+', e.data));
        evtSource.addEventListener('file_created', (e) => addEvent('FILE', e.data));
        evtSource.addEventListener('file_modified', (e) => addEvent('FILE', e.data));
        evtSource.addEventListener('agent_action', (e) => addEvent('AGENT', e.data));
        evtSource.addEventListener('error', (e) => addEvent('ERROR', e.data));

        function addEvent(type, data) {
            const div = document.createElement('div');
            div.className = 'event';
            const ts = new Date().toLocaleTimeString();
            div.textContent = '[' + ts + '] ' + type + ': ' + (typeof data === 'string' ? data : JSON.stringify(data));
            events.insertBefore(div, events.firstChild);
            if (events.children.length > 100) events.removeChild(events.lastChild);
        }

        evtSource.onerror = () => {
            stateDiv.textContent = 'Disconnected. Reconnecting...';
        };

        // Fetch alerts periodically
        setInterval(async () => {
            try {
                const res = await fetch('/api/v1/loops');
                const data = await res.json();
                if (data.alerts.length > 0) {
                    alertsDiv.innerHTML = data.alerts.map(a =>
                        '<div class="alert">' + a.agent + ': ' + a.action + ' x' + a.count + ' (' + a.severity + ')</div>'
                    ).join('');
                } else {
                    alertsDiv.textContent = 'No loops detected';
                }
            } catch (e) {}
        }, 5000);
    </script>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _send_json(self, data: dict):
        """Send JSON response."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode())


# ── Background thread ────────────────────────────────────────────────────

def _background_worker():
    """Background thread that reads traces and distributes events."""
    while True:
        try:
            # Read new events from trace files
            new_events = trace_reader.read_new_events()

            for event in new_events:
                project = event.get("project", "")

                # Update state machine
                state_machine.update(project, event)

                # Check for loops
                agent = event.get("agent", "")
                action = event.get("event", "")
                if agent:
                    alert = loop_detector.record(agent, action, project)
                    if alert:
                        sse_manager.broadcast({"event": "loop_alert", "data": alert}, project)

                # Broadcast to SSE clients
                sse_manager.broadcast(event, project)

            # Check for paused projects
            paused = state_machine.check_paused()
            for project, new_state in paused.items():
                sse_manager.broadcast({
                    "event": "state_change",
                    "data": {"project": project, "state": new_state},
                }, project)

        except Exception:
            pass

        time.sleep(POLL_INTERVAL)


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="EDMS Real-Time SSE Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port (default: 8765)")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host (default: 0.0.0.0)")
    args = parser.parse_args()

    # Start background worker
    worker = threading.Thread(target=_background_worker, daemon=True)
    worker.start()

    # Start HTTP server
    server = HTTPServer((args.host, args.port), SSEHandler)
    print(f"EDMS Monitor running on http://{args.host}:{args.port}")
    print(f"  SSE stream: http://{args.host}:{args.port}/api/v1/events")
    print(f"  Dashboard:  http://{args.host}:{args.port}/")
    print(f"  Traces dir: {TRACES_DIR}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
