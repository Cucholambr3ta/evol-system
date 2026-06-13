#!/usr/bin/env python3
"""user_model.py — Dialectic user model for Evol-DD Memory v2.0.

Models the *operator*: how they think, what they prefer, what triggers shift
their intent — not just project facts. Inspired by Hermes' Honcho dialectic
user modeling.

Complements the harness auto-memory (user/feedback atoms): this store
*consumes* accumulated feedback to build a structured, queryable profile that
can be injected at session wake-up so context is not repeated each session.
It is a single-operator profile (one JSON document), versioned on each update.

Schema (Honcho-style):
- cognitive_style:    dict[str, float]  e.g. {"analytical": 0.9}
- decision_patterns:  list of {pattern, confidence, evidence_ids, context}
- communication_style: dict[str, float]
- preferences:        dict[str, Any]
- triggers:           list of {trigger, response, context}
- learning_style:     dict[str, Any]

Stdlib-only; no LLM.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# A decision pattern is only promoted to "fixed" once corroborated by at least
# this many distinct pieces of evidence — evidence-based confidence.
MIN_EVIDENCE_TO_FIX = 2


class UserModelStore:
    """Single-operator dialectic profile, versioned per update.

    Usage:
        um = UserModelStore()
        um.set_preference("format", "markdown sin emojis")
        um.add_trigger("caveman", "modo terse", "usuario pide caveman")
        um.observe_decision_pattern("exige cero deuda tecnica", evidence_id="s1")
        ctx = um.wake_up_summary()
    """

    def __init__(self, memory_dir: str | None = None):
        if memory_dir is None:
            memory_dir = os.environ.get(
                "EVOL_MEMORY_DIR", os.path.expanduser("~/.evol/memory")
            )
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._file = self.memory_dir / "user_model.json"
        self._model: dict[str, Any] = self._default()
        self._load()

    # -- persistence -------------------------------------------------------

    @staticmethod
    def _default() -> dict[str, Any]:
        now = datetime.now().isoformat()
        return {
            "cognitive_style": {},
            "decision_patterns": [],
            "communication_style": {},
            "preferences": {},
            "triggers": [],
            "learning_style": {},
            "version": 0,
            "created_at": now,
            "updated_at": now,
        }

    def _load(self) -> None:
        if self._file.exists():
            try:
                self._model = json.loads(self._file.read_text())
            except (json.JSONDecodeError, OSError):
                self._model = self._default()

    def _save(self) -> None:
        self._model["version"] += 1
        self._model["updated_at"] = datetime.now().isoformat()
        self._file.write_text(json.dumps(self._model, ensure_ascii=False, indent=2))

    # -- mutators ----------------------------------------------------------

    def set_preference(self, key: str, value: Any) -> None:
        self._model["preferences"][key] = value
        self._save()

    def set_cognitive_style(self, **scores: float) -> None:
        self._model["cognitive_style"].update(scores)
        self._save()

    def set_communication_style(self, **scores: float) -> None:
        self._model["communication_style"].update(scores)
        self._save()

    def set_learning_style(self, **values: Any) -> None:
        self._model["learning_style"].update(values)
        self._save()

    def add_trigger(self, trigger: str, response: str, context: str = "") -> None:
        """Add or replace a trigger->response mapping."""
        triggers = [t for t in self._model["triggers"] if t["trigger"] != trigger]
        triggers.append({"trigger": trigger, "response": response, "context": context})
        self._model["triggers"] = triggers
        self._save()

    def observe_decision_pattern(
        self, pattern: str, evidence_id: str = "", context: str = ""
    ) -> dict[str, Any]:
        """Record (or reinforce) a decision pattern.

        Confidence is evidence-based: it grows with the number of distinct
        evidence ids and only counts as "fixed" once it reaches
        MIN_EVIDENCE_TO_FIX. Returns the updated pattern entry.
        """
        existing = next(
            (p for p in self._model["decision_patterns"] if p["pattern"] == pattern),
            None,
        )
        if existing is None:
            existing = {
                "pattern": pattern,
                "evidence_ids": [],
                "context": context,
                "confidence": 0.0,
                "fixed": False,
            }
            self._model["decision_patterns"].append(existing)
        if evidence_id and evidence_id not in existing["evidence_ids"]:
            existing["evidence_ids"].append(evidence_id)
        if context:
            existing["context"] = context
        n = len(existing["evidence_ids"])
        existing["confidence"] = round(min(0.5 + 0.25 * n, 0.99), 3) if n else 0.5
        existing["fixed"] = n >= MIN_EVIDENCE_TO_FIX
        self._save()
        return existing

    # -- queries -----------------------------------------------------------

    def get(self) -> dict[str, Any]:
        """Full profile (a copy)."""
        return json.loads(json.dumps(self._model))

    def detect_triggers(self, query: str) -> list[dict[str, Any]]:
        """Triggers whose keyword appears in the query (case-insensitive)."""
        q = query.lower()
        return [t for t in self._model["triggers"] if t["trigger"].lower() in q]

    def fixed_patterns(self) -> list[dict[str, Any]]:
        """Decision patterns corroborated by enough evidence."""
        return [p for p in self._model["decision_patterns"] if p.get("fixed")]

    def wake_up_summary(self) -> str:
        """Compact human-readable profile for session wake-up injection."""
        m = self._model
        lines: list[str] = []
        if m["preferences"]:
            prefs = ", ".join(f"{k}={v}" for k, v in m["preferences"].items())
            lines.append(f"Preferencias: {prefs}")
        if m["triggers"]:
            trg = ", ".join(f"'{t['trigger']}'->{t['response']}" for t in m["triggers"])
            lines.append(f"Triggers: {trg}")
        fixed = self.fixed_patterns()
        if fixed:
            pats = "; ".join(p["pattern"] for p in fixed)
            lines.append(f"Patrones de decision: {pats}")
        if m["cognitive_style"]:
            cog = ", ".join(f"{k}={v}" for k, v in m["cognitive_style"].items())
            lines.append(f"Estilo cognitivo: {cog}")
        return "\n".join(lines) if lines else "(perfil de operador vacio)"

    def stats(self) -> dict[str, Any]:
        m = self._model
        return {
            "version": m["version"],
            "preferences": len(m["preferences"]),
            "triggers": len(m["triggers"]),
            "decision_patterns": len(m["decision_patterns"]),
            "fixed_patterns": len(self.fixed_patterns()),
        }
