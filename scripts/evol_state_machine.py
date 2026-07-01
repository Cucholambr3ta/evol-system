#!/usr/bin/env python3
"""EDMS Project State Machine — Active/Paused/Error.

Tracks project activity based on event timestamps.
Transitions:
  Active → Paused: after 10 minutes without events
  Paused → Active: on new event
  Active → Error: after 3+ consecutive errors
  Error → Active: on successful event

Usage:
  from evol_state_machine import StateMachine
  sm = StateMachine()
  sm.update("evol-dd", {"event": "edms_index", "ts": "..."})
  print(sm.get_state("evol-dd"))  # {"state": "active", ...}

CLI:
  python3 evol_state_machine.py status [--project NAME]
  python3 evol_state_machine.py watch [--project NAME]
"""

import json
import sys
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Config ────────────────────────────────────────────────────────────────

PAUSE_THRESHOLD = 600  # 10 minutes
ERROR_THRESHOLD = 3    # consecutive errors before Error state
STATE_FILE = Path(".evol/project-states.json")


class StateMachine:
    """Track project state transitions based on events."""

    def __init__(self):
        self._states: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        """Load persisted states from disk."""
        if STATE_FILE.exists():
            try:
                self._states = json.loads(STATE_FILE.read_text())
            except Exception:
                self._states = {}

    def _save(self):
        """Persist states to disk."""
        try:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATE_FILE.write_text(json.dumps(self._states, indent=2, ensure_ascii=False))
        except Exception:
            pass

    def update(self, project: str, event: dict) -> str:
        """Update state based on new event. Returns current state."""
        with self._lock:
            now = time.time()
            if project not in self._states:
                self._states[project] = {
                    "state": "active",
                    "last_event_ts": now,
                    "last_event_type": event.get("event", "unknown"),
                    "event_count": 0,
                    "error_count": 0,
                    "transitions": [],
                }

            ps = self._states[project]
            old_state = ps["state"]
            ps["last_event_ts"] = now
            ps["last_event_type"] = event.get("event", "unknown")
            ps["event_count"] += 1

            # State transitions
            if event.get("event") == "error":
                ps["error_count"] += 1
                if ps["error_count"] >= ERROR_THRESHOLD and ps["state"] != "error":
                    ps["state"] = "error"
                    ps["transitions"].append({
                        "from": old_state,
                        "to": "error",
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "reason": f"{ps['error_count']} consecutive errors",
                    })
            else:
                if ps["error_count"] > 0:
                    ps["error_count"] = 0
                if ps["state"] != "active":
                    ps["state"] = "active"
                    ps["transitions"].append({
                        "from": old_state,
                        "to": "active",
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "reason": "new event received",
                    })

            # Keep only last 20 transitions
            ps["transitions"] = ps["transitions"][-20:]

            self._save()
            return ps["state"]

    def check_paused(self) -> dict[str, str]:
        """Check if any projects should be paused. Returns changed states."""
        with self._lock:
            now = time.time()
            changed = {}
            for project, ps in self._states.items():
                if ps["state"] == "active":
                    if now - ps["last_event_ts"] > PAUSE_THRESHOLD:
                        old_state = ps["state"]
                        ps["state"] = "paused"
                        ps["transitions"].append({
                            "from": old_state,
                            "to": "paused",
                            "ts": datetime.now(timezone.utc).isoformat(),
                            "reason": f"no events for {int(now - ps['last_event_ts'])}s",
                        })
                        changed[project] = "paused"
                elif ps["state"] == "paused":
                    if now - ps["last_event_ts"] <= PAUSE_THRESHOLD:
                        old_state = ps["state"]
                        ps["state"] = "active"
                        ps["transitions"].append({
                            "from": old_state,
                            "to": "active",
                            "ts": datetime.now(timezone.utc).isoformat(),
                            "reason": "new event received",
                        })
                        changed[project] = "active"

            if changed:
                self._save()
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
                        "last_event_ts": datetime.fromtimestamp(
                            ps["last_event_ts"], tz=timezone.utc
                        ).isoformat(),
                        "last_event_type": ps["last_event_type"],
                        "event_count": ps["event_count"],
                        "error_count": ps["error_count"],
                        "transitions": ps["transitions"][-5:],
                    }
                return {"project": project, "state": "unknown"}
            return {
                p: {
                    "state": ps["state"],
                    "last_event_ts": datetime.fromtimestamp(
                        ps["last_event_ts"], tz=timezone.utc
                    ).isoformat(),
                    "event_count": ps["event_count"],
                }
                for p, ps in self._states.items()
            }

    def reset(self, project: str):
        """Reset state for a project."""
        with self._lock:
            if project in self._states:
                del self._states[project]
                self._save()


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="EDMS Project State Machine")
    sub = parser.add_subparsers(dest="cmd")

    p_status = sub.add_parser("status", help="Show project states")
    p_status.add_argument("--project", default="", help="Filter by project")

    p_watch = sub.add_parser("watch", help="Watch state changes in real-time")
    p_watch.add_argument("--project", default="", help="Filter by project")
    p_watch.add_argument("--interval", type=int, default=5, help="Check interval (seconds)")

    p_reset = sub.add_parser("reset", help="Reset project state")
    p_reset.add_argument("project", help="Project name")

    args = parser.parse_args()

    sm = StateMachine()

    if args.cmd == "status":
        state = sm.get_state(args.project)
        print(json.dumps(state, indent=2, ensure_ascii=False))

    elif args.cmd == "watch":
        print(f"Watching project states (interval: {args.interval}s)...")
        print("Press Ctrl+C to stop.\n")
        try:
            while True:
                changed = sm.check_paused()
                if changed:
                    for project, new_state in changed.items():
                        ts = datetime.now().strftime("%H:%M:%S")
                        print(f"[{ts}] {project}: → {new_state}")

                # Print current states
                states = sm.get_state(args.project)
                for p, s in states.items():
                    ts = datetime.now().strftime("%H:%M:%S")
                    print(f"[{ts}] {p}: {s['state']} (events: {s['event_count']})")

                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopped.")

    elif args.cmd == "reset":
        sm.reset(args.project)
        print(f"Reset state for {args.project}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
