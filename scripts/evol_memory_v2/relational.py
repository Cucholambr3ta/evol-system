"""
Relational intelligence for EDMS Memory v2.0.

Computes pre-computed relationship scores between agents, projects, and concepts.
Useful for team composition and task routing.

Part of EDMS Memory v2.0 Phase 4 - Portability and Ecosystem.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class RelationshipScore:
    """A pre-computed relationship score."""
    source_id: str
    target_id: str
    relation_type: str  # "agent_agent", "agent_project", "concept_concept"
    score: float  # 0-1, higher = stronger relationship
    confidence: float  # 0-1, higher = more confident
    evidence_count: int = 0
    last_interaction: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class RelationalIntelligence:
    """
    Relational intelligence engine.

    Computes and maintains pre-computed relationship scores between
    agents, projects, and concepts based on interaction patterns.

    Usage:
        ri = RelationalIntelligence()
        ri.record_interaction("evol-builder", "evol-qa", "code_review")
        ri.record_interaction("evol-builder", "evol-sec", "security_audit")

        scores = ri.get_relationship_scores("evol-builder")
        # Returns list of RelationshipScore objects
    """

    def __init__(self):
        # Interactions: (source, target, type) -> count
        self._interactions: dict[tuple[str, str, str], int] = defaultdict(int)

        # Timestamps: (source, target, type) -> last timestamp
        self._timestamps: dict[tuple[str, str, str], str] = {}

        # Relationship scores cache
        self._scores: dict[tuple[str, str, str], RelationshipScore] = {}

    def record_interaction(
        self,
        source_id: str,
        target_id: str,
        interaction_type: str,
        weight: float = 1.0,
    ) -> None:
        """
        Record an interaction between two entities.

        Args:
            source_id: Source entity ID (e.g., agent name)
            target_id: Target entity ID
            interaction_type: Type of interaction (e.g., "code_review")
            weight: Interaction weight (default 1.0)
        """
        key = (source_id, target_id, interaction_type)
        self._interactions[key] += weight
        self._timestamps[key] = datetime.now().isoformat()

        # Invalidate cache for this pair
        if key in self._scores:
            del self._scores[key]

    def get_relationship_scores(
        self,
        entity_id: str,
        min_score: float = 0.0,
    ) -> list[RelationshipScore]:
        """
        Get relationship scores for an entity.

        Args:
            entity_id: Entity to get scores for
            min_score: Minimum score threshold

        Returns:
            List of RelationshipScore objects
        """
        scores = []

        # Find all interactions involving this entity
        for (source, target, rel_type), count in self._interactions.items():
            if source == entity_id or target == entity_id:
                key = (source, target, rel_type)

                # Calculate or retrieve cached score
                if key not in self._scores:
                    self._scores[key] = self._calculate_score(source, target, rel_type)

                score = self._scores[key]
                if score.score >= min_score:
                    scores.append(score)

        # Sort by score descending
        scores.sort(key=lambda s: s.score, reverse=True)

        return scores

    def _calculate_score(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
    ) -> RelationshipScore:
        """Calculate relationship score based on interactions."""
        key = (source_id, target_id, relation_type)
        count = self._interactions.get(key, 0)
        last_ts = self._timestamps.get(key, "")

        # Score calculation: normalize count to 0-1 range
        # Using logarithmic scale to handle varying interaction counts
        import math
        score = min(math.log1p(count) / math.log1p(100), 1.0)

        # Confidence based on evidence count
        confidence = min(count / 10, 1.0)

        return RelationshipScore(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            score=round(score, 3),
            confidence=round(confidence, 3),
            evidence_count=count,
            last_interaction=last_ts,
        )

    def get_top_relationships(
        self,
        entity_id: str,
        top_k: int = 5,
    ) -> list[RelationshipScore]:
        """
        Get top-k relationships for an entity.

        Args:
            entity_id: Entity to get relationships for
            top_k: Number of top relationships to return

        Returns:
            List of top RelationshipScore objects
        """
        all_scores = self.get_relationship_scores(entity_id)
        return all_scores[:top_k]

    def get_mutual_relationships(
        self,
        entity1_id: str,
        entity2_id: str,
    ) -> list[RelationshipScore]:
        """
        Get mutual relationships between two entities.

        Args:
            entity1_id: First entity
            entity2_id: Second entity

        Returns:
            List of RelationshipScore objects for both directions
        """
        scores = []

        # Check both directions
        for (source, target, rel_type), count in self._interactions.items():
            if (source == entity1_id and target == entity2_id) or \
               (source == entity2_id and target == entity1_id):
                key = (source, target, rel_type)
                if key not in self._scores:
                    self._scores[key] = self._calculate_score(source, target, rel_type)
                scores.append(self._scores[key])

        return scores

    def suggest_collaborators(
        self,
        agent_id: str,
        task_type: str,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Suggest collaborators for a task based on relationship scores.

        Args:
            agent_id: Agent looking for collaborators
            task_type: Type of task (e.g., "code_review", "security_audit")
            top_k: Number of suggestions

        Returns:
            List of suggested collaborator dicts
        """
        suggestions = []

        # Find agents with high interaction scores for this task type
        for (source, target, rel_type), count in self._interactions.items():
            if rel_type == task_type and source == agent_id:
                key = (source, target, rel_type)
                if key not in self._scores:
                    self._scores[key] = self._calculate_score(source, target, rel_type)

                score = self._scores[key]
                suggestions.append({
                    "agent_id": target,
                    "score": score.score,
                    "confidence": score.confidence,
                    "evidence_count": score.evidence_count,
                    "reason": f"High interaction count ({count}) for {task_type}",
                })

        # Sort by score descending
        suggestions.sort(key=lambda s: s["score"], reverse=True)

        return suggestions[:top_k]

    def stats(self) -> dict[str, Any]:
        """Get relational intelligence statistics."""
        total_interactions = sum(self._interactions.values())
        unique_pairs = len(self._interactions)
        unique_entities = set()
        for source, target, _ in self._interactions.keys():
            unique_entities.add(source)
            unique_entities.add(target)

        # Count by relation type
        by_type: dict[str, int] = defaultdict(int)
        for _, _, rel_type in self._interactions.keys():
            by_type[rel_type] += 1

        return {
            "total_interactions": total_interactions,
            "unique_pairs": unique_pairs,
            "unique_entities": len(unique_entities),
            "by_relation_type": dict(by_type),
            "cached_scores": len(self._scores),
        }

    # -----------------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Save relational intelligence to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "interactions": [
                {
                    "source": source,
                    "target": target,
                    "relation_type": rel_type,
                    "count": count,
                    "last_interaction": self._timestamps.get((source, target, rel_type), ""),
                }
                for (source, target, rel_type), count in self._interactions.items()
            ],
        }

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> RelationalIntelligence:
        """Load relational intelligence from JSON file."""
        path = Path(path)
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())
        ri = cls()

        for interaction in data.get("interactions", []):
            key = (
                interaction["source"],
                interaction["target"],
                interaction["relation_type"],
            )
            ri._interactions[key] = interaction.get("count", 1)
            if "last_interaction" in interaction:
                ri._timestamps[key] = interaction["last_interaction"]

        return ri
