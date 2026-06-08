"""
Conflict detector for EDMS Memory v2.0.

Identifies contradictory memories and suggests resolutions.
Implements predicate contradiction detection and temporal inconsistency detection.

Part of EDMS Memory v2.0 Phase 3 - Consolidation and Dreaming.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Conflict:
    """A detected conflict between memories."""
    id: str
    memory_ids: list[str]
    conflict_type: str  # "predicate", "temporal", "factual"
    description: str
    severity: float  # 0-1, higher = more severe
    created_at: str = ""
    resolved: bool = False
    resolution: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class ConflictResolution:
    """Suggested resolution for a conflict."""
    conflict_id: str
    strategy: str  # "keep_latest", "keep_highest_confidence", "merge", "manual"
    description: str
    confidence: float
    action: str  # What to do


class ConflictDetector:
    """
    Conflict detector for memory systems.

    Identifies contradictory memories and suggests resolutions.
    Implements predicate contradiction detection and temporal inconsistency detection.

    Usage:
        detector = ConflictDetector()
        conflicts = detector.detect(memories)
        resolutions = detector.suggest_resolution(conflicts)
    """

    def __init__(
        self,
        negation_patterns: list[str] | None = None,
        temporal_window_days: int = 7,
    ):
        self.temporal_window_days = temporal_window_days

        # Negation patterns for predicate contradiction detection
        self.negation_patterns = negation_patterns or [
            r"no\s+(?:es|son|está|están|fue|fueron|ha|hayan)",
            r"nunca",
            r"jamás",
            r"ni\s+.*\s+ni",
            r"tampoco",
        ]

        # Detected conflicts
        self._conflicts: dict[str, Conflict] = {}

    def detect(self, memories: list[dict[str, Any]]) -> list[Conflict]:
        """
        Detect conflicts in memories.

        Args:
            memories: List of memory dicts with id, text, metadata, etc.

        Returns:
            List of Conflict objects
        """
        conflicts = []

        # Detect predicate contradictions
        predicate_conflicts = self._detect_predicate_contradictions(memories)
        conflicts.extend(predicate_conflicts)

        # Detect temporal inconsistencies
        temporal_conflicts = self._detect_temporal_inconsistencies(memories)
        conflicts.extend(temporal_conflicts)

        # Detect factual contradictions
        factual_conflicts = self._detect_factual_contradictions(memories)
        conflicts.extend(factual_conflicts)

        # Store conflicts
        for conflict in conflicts:
            self._conflicts[conflict.id] = conflict

        return conflicts

    def _detect_predicate_contradictions(
        self,
        memories: list[dict[str, Any]],
    ) -> list[Conflict]:
        """Detect predicate contradictions (A and not A)."""
        conflicts = []

        # Group by topic (simple: by first few words)
        by_topic: dict[str, list[dict[str, Any]]] = {}
        for mem in memories:
            # Extract topic (first 3 significant words)
            words = mem.get("text", "").lower().split()
            topic_words = [w for w in words if len(w) > 3][:3]
            topic = "_".join(topic_words) if topic_words else "unknown"

            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(mem)

        # Check for negation patterns within each topic
        for topic, topic_mems in by_topic.items():
            if len(topic_mems) < 2:
                continue

            # Find positive and negative statements
            positive = []
            negative = []

            for mem in topic_mems:
                text = mem.get("text", "").lower()
                is_negative = any(
                    re.search(pattern, text) for pattern in self.negation_patterns
                )

                if is_negative:
                    negative.append(mem)
                else:
                    positive.append(mem)

            # If both positive and negative exist, it's a conflict
            if positive and negative:
                conflict_id = f"predicate_{topic}_{hash(str([m.get('id') for m in positive + negative]))}"
                conflict = Conflict(
                    id=conflict_id,
                    memory_ids=[m.get("id", "") for m in positive + negative],
                    conflict_type="predicate",
                    description=f"Contradicción de predicado en topic '{topic}': afirmaciones positivas y negativas",
                    severity=0.8,
                    metadata={
                        "positive_count": len(positive),
                        "negative_count": len(negative),
                    },
                )
                conflicts.append(conflict)

        return conflicts

    def _detect_temporal_inconsistencies(
        self,
        memories: list[dict[str, Any]],
    ) -> list[Conflict]:
        """Detect temporal inconsistencies (contradictions over time)."""
        conflicts = []

        # Group by topic
        by_topic: dict[str, list[dict[str, Any]]] = {}
        for mem in memories:
            words = mem.get("text", "").lower().split()
            topic_words = [w for w in words if len(w) > 3][:3]
            topic = "_".join(topic_words) if topic_words else "unknown"

            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(mem)

        # Check for temporal inconsistencies within each topic
        for topic, topic_mems in by_topic.items():
            if len(topic_mems) < 2:
                continue

            # Sort by time
            sorted_mems = sorted(topic_mems, key=lambda m: m.get("created_at", ""))

            # Check for contradictions within temporal window
            for i in range(len(sorted_mems)):
                for j in range(i + 1, len(sorted_mems)):
                    mem1 = sorted_mems[i]
                    mem2 = sorted_mems[j]

                    # Check if within temporal window
                    try:
                        t1 = datetime.fromisoformat(mem1.get("created_at", ""))
                        t2 = datetime.fromisoformat(mem2.get("created_at", ""))
                        days_diff = (t2 - t1).days

                        if days_diff > self.temporal_window_days:
                            continue

                        # Check for contradiction
                        text1 = mem1.get("text", "").lower()
                        text2 = mem2.get("text", "").lower()

                        # Simple contradiction detection: opposite keywords
                        if self._are_contradictory(text1, text2):
                            conflict_id = f"temporal_{topic}_{mem1.get('id', '')}_{mem2.get('id', '')}"
                            conflict = Conflict(
                                id=conflict_id,
                                memory_ids=[mem1.get("id", ""), mem2.get("id", "")],
                                conflict_type="temporal",
                                description=f"Inconsistencia temporal en topic '{topic}' ({days_diff} días de diferencia)",
                                severity=0.6,
                                metadata={
                                    "days_difference": days_diff,
                                    "mem1_date": mem1.get("created_at", ""),
                                    "mem2_date": mem2.get("created_at", ""),
                                },
                            )
                            conflicts.append(conflict)

                    except (ValueError, TypeError):
                        continue

        return conflicts

    def _are_contradictory(self, text1: str, text2: str) -> bool:
        """Check if two texts are contradictory."""
        # Simple heuristic: check for negation patterns
        text1_neg = any(
            re.search(pattern, text1) for pattern in self.negation_patterns
        )
        text2_neg = any(
            re.search(pattern, text2) for pattern in self.negation_patterns
        )

        # If one is negative and the other is not, check for common keywords
        if text1_neg != text2_neg:
            words1 = set(text1.split())
            words2 = set(text2.split())
            common = words1 & words2

            # If they share significant keywords, likely contradictory
            if len(common) >= 3:
                return True

        return False

    def _detect_factual_contradictions(
        self,
        memories: list[dict[str, Any]],
    ) -> list[Conflict]:
        """Detect factual contradictions (same topic, different values)."""
        conflicts = []

        # Group by topic
        by_topic: dict[str, list[dict[str, Any]]] = {}
        for mem in memories:
            words = mem.get("text", "").lower().split()
            topic_words = [w for w in words if len(w) > 3][:3]
            topic = "_".join(topic_words) if topic_words else "unknown"

            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(mem)

        # Check for factual contradictions within each topic
        for topic, topic_mems in by_topic.items():
            if len(topic_mems) < 2:
                continue

            # Check for different values (simple: different numbers)
            numbers: list[tuple[str, list[int]]] = []
            for mem in topic_mems:
                text = mem.get("text", "")
                nums = re.findall(r"\d+", text)
                if nums:
                    numbers.append((mem.get("id", ""), [int(n) for n in nums]))

            # If different numbers for same topic, it's a conflict
            if len(numbers) >= 2:
                all_nums = [n for _, nums in numbers for n in nums]
                if len(set(all_nums)) > 1:
                    conflict_id = f"factual_{topic}_{hash(str([m.get('id') for m in topic_mems]))}"
                    conflict = Conflict(
                        id=conflict_id,
                        memory_ids=[m.get("id", "") for m in topic_mems],
                        conflict_type="factual",
                        description=f"Contradicción factual en topic '{topic}': diferentes valores numéricos",
                        severity=0.7,
                        metadata={"values": {mid: nums for mid, nums in numbers}},
                    )
                    conflicts.append(conflict)

        return conflicts

    def suggest_resolution(self, conflict: Conflict) -> ConflictResolution:
        """
        Suggest resolution for a conflict.

        Args:
            conflict: Conflict to resolve

        Returns:
            ConflictResolution with suggested action
        """
        if conflict.conflict_type == "predicate":
            return ConflictResolution(
                conflict_id=conflict.id,
                strategy="keep_latest",
                description="Mantener la afirmación más reciente",
                confidence=0.7,
                action="Eliminar memorias contradictorias más antiguas",
            )
        elif conflict.conflict_type == "temporal":
            return ConflictResolution(
                conflict_id=conflict.id,
                strategy="keep_highest_confidence",
                description="Mantener la memoria con mayor confianza",
                confidence=0.6,
                action="Eliminar memorias con menor confianza",
            )
        elif conflict.conflict_type == "factual":
            return ConflictResolution(
                conflict_id=conflict.id,
                strategy="manual",
                description="Revisión manual requerida para contradicciones factuales",
                confidence=0.5,
                action="Marcar para revisión manual",
            )
        else:
            return ConflictResolution(
                conflict_id=conflict.id,
                strategy="manual",
                description="Tipo de conflicto desconocido",
                confidence=0.3,
                action="Marcar para revisión manual",
            )

    def get_conflicts(self) -> list[Conflict]:
        """Get all detected conflicts."""
        return list(self._conflicts.values())

    def get_unresolved_conflicts(self) -> list[Conflict]:
        """Get unresolved conflicts."""
        return [c for c in self._conflicts.values() if not c.resolved]

    def resolve_conflict(self, conflict_id: str, resolution: str) -> bool:
        """
        Mark a conflict as resolved.

        Args:
            conflict_id: ID of conflict to resolve
            resolution: Resolution description

        Returns:
            True if resolved, False if not found
        """
        if conflict_id not in self._conflicts:
            return False

        self._conflicts[conflict_id].resolved = True
        self._conflicts[conflict_id].resolution = resolution
        return True

    def stats(self) -> dict[str, Any]:
        """Get conflict detector statistics."""
        conflicts = list(self._conflicts.values())
        type_counts = {}
        for c in conflicts:
            type_counts[c.conflict_type] = type_counts.get(c.conflict_type, 0) + 1

        return {
            "total_conflicts": len(conflicts),
            "unresolved": len([c for c in conflicts if not c.resolved]),
            "by_type": type_counts,
            "avg_severity": round(
                sum(c.severity for c in conflicts) / max(len(conflicts), 1), 3
            ),
        }

    # -----------------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Save conflicts to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "conflicts": [
                {
                    "id": c.id,
                    "memory_ids": c.memory_ids,
                    "conflict_type": c.conflict_type,
                    "description": c.description,
                    "severity": c.severity,
                    "created_at": c.created_at,
                    "resolved": c.resolved,
                    "resolution": c.resolution,
                }
                for c in self._conflicts.values()
            ]
        }

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> ConflictDetector:
        """Load conflicts from JSON file."""
        path = Path(path)
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())
        detector = cls()

        for conflict_data in data.get("conflicts", []):
            conflict = Conflict(
                id=conflict_data["id"],
                memory_ids=conflict_data.get("memory_ids", []),
                conflict_type=conflict_data.get("conflict_type", "factual"),
                description=conflict_data.get("description", ""),
                severity=conflict_data.get("severity", 0.5),
                created_at=conflict_data.get("created_at", ""),
                resolved=conflict_data.get("resolved", False),
                resolution=conflict_data.get("resolution", ""),
            )
            detector._conflicts[conflict.id] = conflict

        return detector
