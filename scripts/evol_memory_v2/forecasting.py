"""
Forecasting engine for EDMS Memory v2.0.

Phase 3 of dreaming consolidation: after memories are condensed into insights,
detect *recurring* patterns across sprints/phases and project the next likely
occurrence as a predictive memory.

Unlike the other engines this looks forward, not backward. It is the only
forward-looking tier in EDMS and — per the ecosystem survey of 20 memory
systems — a capability only Skales had.

Default implementation is pure stdlib and deterministic: confidence is derived
from observed frequency, no LLM. An optional LLM path is gated behind the
``EVOL_MEMORY_LLM`` env var (reserved; not implemented here).

Inspired by Skales' 3-phase overnight consolidation (condensation, synthesis,
forecasting).
"""

from __future__ import annotations

import hashlib
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .reflection import MemoryItem


@dataclass
class Prediction:
    """A forward-looking, derived memory.

    Stored as a ``type=prediction`` atom. ``confidence`` reflects how strongly
    the underlying pattern recurred; ``horizon`` is a human-readable scope
    (e.g. "next sprint"); ``evidence_ids`` are the source memory ids.
    """
    id: str
    content: str
    confidence: float
    horizon: str
    evidence_ids: list[str] = field(default_factory=list)
    source: str = "forecasting"
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_atom_metadata(self) -> dict[str, Any]:
        """Metadata dict for persisting via VerbatimStore."""
        return {
            "tipo": "prediction",
            "confidence": self.confidence,
            "horizon": self.horizon,
            "source": self.source,
            "evidence_ids": self.evidence_ids,
            **self.metadata,
        }


# Heuristic detectors: extract a recurrence key from a memory's metadata/text.
# Each returns a short label or None. Recurrence of the same label across
# distinct sprints/phases is the prediction signal.
_DISCIPLINE_RE = re.compile(
    r"\b(sdd|fdd|ddd|bdd|atdd|tdd|stdd|secdd|threat|odd|uxdd|a11y|rdd|pdd|"
    r"chaos|mdd|esdd|ccdd|apivdd|slo|iodd|compliance|privacy)\b",
    re.IGNORECASE,
)


def _sprint_of(item: MemoryItem) -> str | None:
    """Sprint bucket for an item, from metadata.sprint or 'sprint-NN' in text."""
    sprint = item.metadata.get("sprint") or item.metadata.get("sprint_id")
    if sprint:
        return f"sprint-{sprint}"
    m = re.search(r"sprint[-\s]?(\d+)", item.text, re.IGNORECASE)
    return f"sprint-{m.group(1)}" if m else None


class ForecastEngine:
    """Detect recurring patterns and emit predictive memories.

    Stdlib-only heuristic. ``forecast()`` groups memories by a recurrence key
    (tipo, discipline, or failing gate) and, when a key recurs across at least
    ``min_occurrences`` distinct sprints, emits a Prediction whose confidence
    grows with recurrence count and sprint coverage.
    """

    def __init__(
        self,
        min_occurrences: int = 2,
        min_confidence: float = 0.5,
    ):
        self.min_occurrences = min_occurrences
        self.min_confidence = min_confidence
        self._predictions: dict[str, Prediction] = {}

    # -- key extraction ----------------------------------------------------

    def _recurrence_keys(self, item: MemoryItem) -> list[tuple[str, str]]:
        """(kind, label) keys a memory contributes to. Multiple allowed."""
        keys: list[tuple[str, str]] = []
        tipo = item.metadata.get("tipo")
        if tipo in ("riesgo", "leccion"):
            keys.append((tipo, tipo))  # recurring risks / lessons
        disc = _DISCIPLINE_RE.search(item.text)
        if disc:
            keys.append(("discipline", disc.group(1).lower()))
        if item.metadata.get("gate_failed") or re.search(
            r"\bgate\b.*\b(fall|fail|bloque|block)", item.text, re.IGNORECASE
        ):
            keys.append(("gate", "gate_failure"))
        return keys

    # -- public API --------------------------------------------------------

    def forecast(
        self,
        memories: list[MemoryItem],
        history: list[Any] | None = None,
    ) -> list[Prediction]:
        """Project recurring patterns forward into predictions.

        Args:
            memories: Consolidated memory items (same type dreaming feeds in).
            history: Optional prior DreamSession list (reserved; lets the LLM
                path reason over past runs). Unused by the stdlib heuristic.

        Returns:
            Predictions above ``min_confidence``.
        """
        if os.environ.get("EVOL_MEMORY_LLM"):
            # Reserved hook for an LLM-backed forecaster. Falls through to the
            # deterministic heuristic until implemented.
            pass

        # Group source ids and sprint coverage per recurrence key.
        by_key: dict[tuple[str, str], dict[str, Any]] = defaultdict(
            lambda: {"ids": [], "sprints": set()}
        )
        for item in memories:
            sprint = _sprint_of(item)
            for key in self._recurrence_keys(item):
                bucket = by_key[key]
                bucket["ids"].append(item.id)
                if sprint:
                    bucket["sprints"].add(sprint)

        predictions: list[Prediction] = []
        for (kind, label), bucket in by_key.items():
            occurrences = len(bucket["ids"])
            sprint_span = max(len(bucket["sprints"]), 1)
            if occurrences < self.min_occurrences:
                continue
            confidence = self._confidence(occurrences, sprint_span)
            if confidence < self.min_confidence:
                continue
            content = self._phrase(kind, label, occurrences, sprint_span)
            pred = Prediction(
                id=self._make_id(kind, label),
                content=content,
                confidence=confidence,
                horizon="next sprint",
                evidence_ids=bucket["ids"],
                metadata={"kind": kind, "label": label, "occurrences": occurrences},
            )
            self._predictions[pred.id] = pred
            predictions.append(pred)

        predictions.sort(key=lambda p: p.confidence, reverse=True)
        return predictions

    def get_predictions(
        self, min_confidence: float | None = None
    ) -> list[Prediction]:
        preds = list(self._predictions.values())
        if min_confidence is not None:
            preds = [p for p in preds if p.confidence >= min_confidence]
        return sorted(preds, key=lambda p: p.confidence, reverse=True)

    def stats(self) -> dict[str, Any]:
        preds = list(self._predictions.values())
        return {
            "total_predictions": len(preds),
            "avg_confidence": round(
                sum(p.confidence for p in preds) / len(preds), 3
            ) if preds else 0.0,
            "by_kind": {
                k: len([p for p in preds if p.metadata.get("kind") == k])
                for k in {p.metadata.get("kind") for p in preds}
            } if preds else {},
        }

    # -- helpers -----------------------------------------------------------

    @staticmethod
    def _confidence(occurrences: int, sprint_span: int) -> float:
        """Frequency-based confidence in (0, 1].

        More occurrences and broader sprint coverage => higher confidence,
        with diminishing returns. Deterministic, no LLM.
        """
        # base grows with occurrences (saturating), boosted by sprint coverage
        base = 1.0 - (1.0 / (occurrences + 1))          # 2->0.67, 3->0.75, ...
        span_boost = min(sprint_span, 4) / 8.0           # up to +0.5
        return round(min(base + span_boost, 0.99), 3)

    @staticmethod
    def _phrase(kind: str, label: str, occurrences: int, sprint_span: int) -> str:
        span = f"{sprint_span} sprint(s)" if sprint_span > 1 else "this sprint"
        if kind == "discipline":
            return (
                f"La disciplina '{label}' aparece {occurrences} veces en {span}; "
                f"probablemente vuelva a requerirse en el proximo sprint."
            )
        if kind == "gate":
            return (
                f"Gates fallaron/bloquearon {occurrences} veces en {span}; "
                f"revisar prerrequisitos antes del proximo gate."
            )
        if kind == "riesgo":
            return (
                f"Riesgo recurrente ({occurrences} registros en {span}); "
                f"probable reaparicion en el proximo sprint."
            )
        if kind == "leccion":
            return (
                f"Leccion recurrente ({occurrences} registros en {span}); "
                f"aplicar proactivamente en el proximo sprint."
            )
        return f"Patron '{label}' recurrente ({occurrences} en {span})."

    @staticmethod
    def _make_id(kind: str, label: str) -> str:
        h = hashlib.sha256(f"{kind}:{label}".encode()).hexdigest()[:12]
        return f"pred_{h}"
