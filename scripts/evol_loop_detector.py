#!/usr/bin/env python3
"""EDMS Agent Loop Detector — detect repeated actions (token overconsumption).

Monitors agent actions in a sliding window and alerts when the same
agent performs the same action repeatedly (indicating a loop).

Usage:
  from evol_loop_detector import LoopDetector
  ld = LoopDetector()
  alert = ld.record("evol-builder", "edms_index", "evol-dd")
  if alert:
      print(f"LOOP DETECTED: {alert}")

CLI:
  python3 evol_loop_detector.py status [--project NAME]
  python3 evol_loop_detector.py record AGENT ACTION [--project NAME]
  python3 evol_loop_detector.py alerts [--project NAME]
"""

import json
import sys
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Config ────────────────────────────────────────────────────────────────

WINDOW = 300       # 5 minutes sliding window
THRESHOLD = 3      # same action N+ times = loop
CRITICAL = 5       # same action N+ times = critical loop
ALERTS_FILE = Path(".evol/loop-alerts.json")


class LoopDetector:
    """Detect agent loops (repeated actions in short window)."""

    def __init__(self, window: int = WINDOW, threshold: int = THRESHOLD):
        self._actions: dict[str, list[dict]] = {}
        self._alerts: list[dict] = []
        self._window = window
        self._threshold = threshold
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        """Load persisted alerts from disk."""
        if ALERTS_FILE.exists():
            try:
                self._alerts = json.loads(ALERTS_FILE.read_text())
            except Exception:
                self._alerts = []

    def _save(self):
        """Persist alerts to disk."""
        try:
            ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            # Keep only last 100 alerts
            alerts_to_save = self._alerts[-100:]
            ALERTS_FILE.write_text(json.dumps(alerts_to_save, indent=2, ensure_ascii=False))
        except Exception:
            pass

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
                if now - a["ts"] < self._window
            ]

            # Count actions in window
            action_counts: dict[str, int] = {}
            for a in self._actions[key]:
                action_counts[a["action"]] = action_counts.get(a["action"], 0) + 1

            # Check for loop
            for action_name, count in action_counts.items():
                if count >= self._threshold:
                    severity = "critical" if count >= CRITICAL else "warning"
                    alert = {
                        "agent": agent,
                        "project": project,
                        "action": action_name,
                        "count": count,
                        "window": self._window,
                        "threshold": self._threshold,
                        "severity": severity,
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "message": f"{agent} performed {action_name} {count} times in {self._window}s",
                    }
                    self._alerts.append(alert)
                    self._save()
                    return alert

            return None

    def get_alerts(self, project: str = "", severity: str = "", limit: int = 20) -> list[dict]:
        """Get recent loop alerts."""
        with self._lock:
            alerts = self._alerts
            if project:
                alerts = [a for a in alerts if a.get("project") == project]
            if severity:
                alerts = [a for a in alerts if a.get("severity") == severity]
            return alerts[-limit:]

    def get_agent_stats(self, project: str = "") -> dict:
        """Get action statistics per agent."""
        with self._lock:
            stats: dict[str, dict] = {}
            for key, actions in self._actions.items():
                agent, proj = key.split(":", 1) if ":" in key else (key, "")
                if project and proj != project:
                    continue

                now = time.time()
                recent = [a for a in actions if now - a["ts"] < self._window]

                if agent not in stats:
                    stats[agent] = {
                        "total_actions": len(recent),
                        "actions": {},
                        "last_action_ts": None,
                    }

                for a in recent:
                    action = a["action"]
                    stats[agent]["actions"][action] = stats[agent]["actions"].get(action, 0) + 1

                if recent:
                    last_ts = max(a["ts"] for a in recent)
                    stats[agent]["last_action_ts"] = datetime.fromtimestamp(
                        last_ts, tz=timezone.utc
                    ).isoformat()

            return stats

    def clear_alerts(self, project: str = ""):
        """Clear alerts for a project."""
        with self._lock:
            if project:
                self._alerts = [a for a in self._alerts if a.get("project") != project]
            else:
                self._alerts = []
            self._save()


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="EDMS Agent Loop Detector")
    sub = parser.add_subparsers(dest="cmd")

    p_status = sub.add_parser("status", help="Show agent statistics")
    p_status.add_argument("--project", default="", help="Filter by project")

    p_record = sub.add_parser("record", help="Record an agent action")
    p_record.add_argument("agent", help="Agent name")
    p_record.add_argument("action", help="Action name")
    p_record.add_argument("--project", default="", help="Project name")

    p_alerts = sub.add_parser("alerts", help="Show loop alerts")
    p_alerts.add_argument("--project", default="", help="Filter by project")
    p_alerts.add_argument("--severity", default="", help="Filter by severity")
    p_alerts.add_argument("--limit", type=int, default=10, help="Max alerts")

    p_clear = sub.add_parser("clear", help="Clear alerts")
    p_clear.add_argument("--project", default="", help="Filter by project")

    args = parser.parse_args()

    ld = LoopDetector()

    if args.cmd == "status":
        stats = ld.get_agent_stats(args.project)
        if stats:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print("No agent activity recorded yet.")

    elif args.cmd == "record":
        alert = ld.record(args.agent, args.action, args.project)
        if alert:
            print(f"LOOP DETECTED: {alert['message']}")
            print(json.dumps(alert, indent=2, ensure_ascii=False))
        else:
            print(f"Recorded: {args.agent} → {args.action}")

    elif args.cmd == "alerts":
        alerts = ld.get_alerts(args.project, args.severity, args.limit)
        if alerts:
            print(json.dumps(alerts, indent=2, ensure_ascii=False))
        else:
            print("No loop alerts.")

    elif args.cmd == "clear":
        ld.clear_alerts(args.project)
        print("Alerts cleared.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
