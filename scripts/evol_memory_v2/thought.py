"""
Thought capture for EDMS Memory v2.0.

Captures the *reasoning* behind a decision — the alternatives that were
evaluated and rejected, and why — not just the winning choice. Per the
ecosystem survey of 20 memory systems, none capture the reasoning process;
this is a greenfield capability.

A Thought is stored as a ``type=thought`` atom via VerbatimStore. When a later
decision contradicts a recorded Thought, ConflictDetector can surface the
original "why" so it is not silently re-litigated.

Stdlib-only; no LLM.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .store import VerbatimStore


@dataclass
class Thought:
    """A captured reasoning step behind a decision.

    Attributes:
        chosen: The option that was selected.
        alternatives: Options that were considered.
        rejected_because: Why the alternatives were not chosen.
        context: What decision/topic this reasoning belongs to.
        evidence_ids: Source memory ids that informed the reasoning.
    """
    chosen: str
    alternatives: list[str] = field(default_factory=list)
    rejected_because: str = ""
    context: str = ""
    evidence_ids: list[str] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_text(self) -> str:
        """Human-readable verbatim form stored in the atom."""
        parts = [f"Decision: {self.chosen}"]
        if self.context:
            parts.append(f"Contexto: {self.context}")
        if self.alternatives:
            parts.append(f"Alternativas evaluadas: {', '.join(self.alternatives)}")
        if self.rejected_because:
            parts.append(f"Descartadas porque: {self.rejected_because}")
        return " | ".join(parts)

    def to_atom_metadata(self) -> dict[str, Any]:
        """Metadata dict for persisting via VerbatimStore."""
        return {
            "tipo": "thought",
            "chosen": self.chosen,
            "alternatives": self.alternatives,
            "rejected_because": self.rejected_because,
            "context": self.context,
            "evidence_ids": self.evidence_ids,
        }


class ThoughtStore:
    """Persist and query captured reasoning (``type=thought`` atoms).

    Thin layer over VerbatimStore so thoughts share verbatim guarantees and
    content-hash dedup with the rest of EDMS.
    """

    def __init__(self, verbatim: VerbatimStore):
        self._verbatim = verbatim

    def capture(self, thought: Thought) -> str:
        """Store a thought; returns its atom id (idempotent by content)."""
        return self._verbatim.write(thought.to_text(), thought.to_atom_metadata())

    def all(self) -> list[dict[str, Any]]:
        """All thought atoms, newest first."""
        items = [
            it for it in self._verbatim.list_items(limit=1000)
            if it.get("metadata", {}).get("tipo") == "thought"
        ]
        items.sort(key=lambda it: it.get("created_at", ""), reverse=True)
        return items

    def for_context(self, context: str) -> list[dict[str, Any]]:
        """Thoughts whose context contains the given substring (case-insensitive)."""
        needle = context.lower()
        return [
            it for it in self.all()
            if needle in it.get("metadata", {}).get("context", "").lower()
        ]

    @staticmethod
    def _id_for(thought: Thought) -> str:
        h = hashlib.sha256(thought.to_text().encode()).hexdigest()[:12]
        return f"thought_{h}"
