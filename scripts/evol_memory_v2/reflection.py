"""
Reflection engine for EDMS Memory v2.0.

Consolidates raw memories into insights during system idle periods.
Implements clustering, summarization, and insight generation.

Part of EDMS Memory v2.0 Phase 3 - Consolidation and Dreaming.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class MemoryItem:
    """A single memory item for reflection."""
    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    importance: float = 0.5

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class Insight:
    """A derived insight from memory consolidation."""
    id: str
    summary: str
    source_ids: list[str]
    insight_type: str  # "pattern", "trend", "contradiction", "evolution"
    confidence: float
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class ReflectionEngine:
    """
    Reflection engine for memory consolidation.

    Analyzes raw memories, identifies patterns, and generates insights
    during system idle periods (dreaming phase).

    Usage:
        engine = ReflectionEngine()
        insights = engine.reflect(memories)
        # insights: list of Insight objects
    """

    def __init__(self, min_cluster_size: int = 3, min_confidence: float = 0.6):
        self.min_cluster_size = min_cluster_size
        self.min_confidence = min_confidence

        # Insight storage
        self._insights: dict[str, Insight] = {}

        # Pattern detection rules
        self._patterns: list[dict[str, Any]] = []

    def reflect(self, memories: list[MemoryItem]) -> list[Insight]:
        """
        Analyze memories and generate insights.

        Args:
            memories: List of MemoryItem objects

        Returns:
            List of Insight objects
        """
        if not memories:
            return []

        # Step 1: Cluster memories by topic
        clusters = self._cluster_by_topic(memories)

        # Step 2: Detect patterns in each cluster
        insights = []
        for cluster_id, cluster_memories in clusters.items():
            # Pattern detection
            patterns = self._detect_patterns(cluster_memories)
            insights.extend(patterns)

            # Trend detection
            trends = self._detect_trends(cluster_memories)
            insights.extend(trends)

            # Evolution detection
            evolutions = self._detect_evolutions(cluster_memories)
            insights.extend(evolutions)

        # Step 3: Cross-cluster analysis
        cross_insights = self._cross_cluster_analysis(clusters)
        insights.extend(cross_insights)

        # Step 4: Filter by confidence
        valid_insights = [
            i for i in insights if i.confidence >= self.min_confidence
        ]

        # Store insights
        for insight in valid_insights:
            self._insights[insight.id] = insight

        return valid_insights

    def _cluster_by_topic(self, memories: list[MemoryItem]) -> dict[str, list[MemoryItem]]:
        """
        Cluster memories by topic similarity.

        Simple approach: group by keyword co-occurrence.
        """
        # Extract keywords from each memory
        memory_keywords: dict[str, set[str]] = {}
        for mem in memories:
            keywords = self._extract_keywords(mem.text)
            memory_keywords[mem.id] = keywords

        # Build co-occurrence matrix
        co_occur: dict[tuple[str, str], int] = defaultdict(int)
        for i, mem1 in enumerate(memories):
            for j, mem2 in enumerate(memories[i + 1:], i + 1):
                common = memory_keywords[mem1.id] & memory_keywords[mem2.id]
                if common:
                    key = tuple(sorted([mem1.id, mem2.id]))
                    co_occur[key] = len(common)

        # Simple clustering: group memories with high co-occurrence
        clusters: dict[str, list[MemoryItem]] = {}
        assigned: set[str] = set()

        for mem in memories:
            if mem.id in assigned:
                continue

            # Find most similar unassigned memory
            best_match = None
            best_score = 0

            for other in memories:
                if other.id == mem.id or other.id in assigned:
                    continue

                key = tuple(sorted([mem.id, other.id]))
                score = co_occur.get(key, 0)

                if score > best_score:
                    best_score = score
                    best_match = other

            # Create cluster if similarity found
            if best_match and best_score >= 2:
                cluster_id = f"cluster_{mem.id}_{best_match.id}"
                clusters[cluster_id] = [mem, best_match]
                assigned.add(mem.id)
                assigned.add(best_match.id)
            else:
                # Singleton cluster
                clusters[f"singleton_{mem.id}"] = [mem]
                assigned.add(mem.id)

        return clusters

    def _extract_keywords(self, text: str) -> set[str]:
        """Extract keywords from text."""
        # Simple keyword extraction: lowercase, split, filter short words
        words = text.lower().split()
        keywords = set()
        for word in words:
            # Remove punctuation
            word = re.sub(r"[^\w]", "", word)
            if len(word) > 3:
                keywords.add(word)
        return keywords

    def _detect_patterns(self, memories: list[MemoryItem]) -> list[Insight]:
        """Detect repeated patterns in memories."""
        insights = []

        if len(memories) < self.min_cluster_size:
            return insights

        # Count common keywords
        all_keywords: Counter = Counter()
        for mem in memories:
            keywords = self._extract_keywords(mem.text)
            all_keywords.update(keywords)

        # Find keywords appearing in >50% of memories
        threshold = len(memories) * 0.5
        common = {k: v for k, v in all_keywords.items() if v >= threshold}

        if common:
            top_keywords = sorted(common.items(), key=lambda x: x[1], reverse=True)[:5]
            summary = f"Patrón detectado: {', '.join(k for k, _ in top_keywords)}"

            insight = Insight(
                id=f"pattern_{hash(summary)}",
                summary=summary,
                source_ids=[m.id for m in memories],
                insight_type="pattern",
                confidence=min(len(common) / 10, 1.0),
                metadata={"keywords": dict(top_keywords)},
            )
            insights.append(insight)

        return insights

    def _detect_trends(self, memories: list[MemoryItem]) -> list[Insight]:
        """Detect temporal trends in memories."""
        insights = []

        if len(memories) < self.min_cluster_size:
            return insights

        # Sort by creation time
        sorted_mems = sorted(memories, key=lambda m: m.created_at)

        # Check if importance is increasing/decreasing
        importances = [m.importance for m in sorted_mems]
        if len(importances) >= 3:
            # Simple trend: compare first half vs second half
            mid = len(importances) // 2
            first_half_avg = sum(importances[:mid]) / mid
            second_half_avg = sum(importances[mid:]) / (len(importances) - mid)

            if second_half_avg > first_half_avg * 1.2:
                trend = "creciente"
                confidence = min((second_half_avg - first_half_avg) * 2, 1.0)
            elif first_half_avg > second_half_avg * 1.2:
                trend = "decreciente"
                confidence = min((first_half_avg - second_half_avg) * 2, 1.0)
            else:
                trend = "estable"
                confidence = 0.5

            summary = f"Tendencia de importancia: {trend}"
            insight = Insight(
                id=f"trend_{hash(summary)}",
                summary=summary,
                source_ids=[m.id for m in memories],
                insight_type="trend",
                confidence=confidence,
                metadata={
                    "trend": trend,
                    "first_half_avg": round(first_half_avg, 3),
                    "second_half_avg": round(second_half_avg, 3),
                },
            )
            insights.append(insight)

        return insights

    def _detect_evolutions(self, memories: list[MemoryItem]) -> list[Insight]:
        """Detect evolution in memory content."""
        insights = []

        if len(memories) < 2:
            return insights

        # Group by metadata tipo
        by_tipo: dict[str, list[MemoryItem]] = defaultdict(list)
        for mem in memories:
            tipo = mem.metadata.get("tipo", "unknown")
            by_tipo[tipo].append(mem)

        # Check for evolution within each tipo
        for tipo, tipo_mems in by_tipo.items():
            if len(tipo_mems) < 2:
                continue

            # Sort by time
            sorted_mems = sorted(tipo_mems, key=lambda m: m.created_at)

            # Check if content changed significantly
            first_text = sorted_mems[0].text.lower()
            last_text = sorted_mems[-1].text.lower()

            # Simple similarity: word overlap
            first_words = set(first_text.split())
            last_words = set(last_text.split())
            overlap = len(first_words & last_words) / max(len(first_words | last_words), 1)

            if overlap < 0.5:  # Significant change
                summary = f"Evolución detectada en tipo '{tipo}': contenido cambió significativamente"
                insight = Insight(
                    id=f"evolution_{tipo}_{hash(summary)}",
                    summary=summary,
                    source_ids=[m.id for m in tipo_mems],
                    insight_type="evolution",
                    confidence=1.0 - overlap,
                    metadata={"tipo": tipo, "overlap": round(overlap, 3)},
                )
                insights.append(insight)

        return insights

    def _cross_cluster_analysis(self, clusters: dict[str, list[MemoryItem]]) -> list[Insight]:
        """Analyze relationships between clusters."""
        insights = []

        if len(clusters) < 2:
            return insights

        # Find keywords that appear in multiple clusters
        cluster_keywords: dict[str, set[str]] = {}
        for cluster_id, memories in clusters.items():
            keywords = set()
            for mem in memories:
                keywords.update(self._extract_keywords(mem.text))
            cluster_keywords[cluster_id] = keywords

        # Find common keywords between clusters
        cross_patterns: dict[tuple[str, str], set[str]] = {}
        cluster_ids = list(clusters.keys())
        for i, c1 in enumerate(cluster_ids):
            for c2 in cluster_ids[i + 1:]:
                common = cluster_keywords[c1] & cluster_keywords[c2]
                if len(common) >= 3:
                    cross_patterns[(c1, c2)] = common

        # Generate insights for cross-cluster patterns
        for (c1, c2), keywords in cross_patterns.items():
            summary = f"Conexión entre clusters: {', '.join(list(keywords)[:3])}"
            insight = Insight(
                id=f"cross_{hash(summary)}",
                summary=summary,
                source_ids=[m.id for m in clusters[c1] + clusters[c2]],
                insight_type="pattern",
                confidence=min(len(keywords) / 10, 1.0),
                metadata={"clusters": [c1, c2], "common_keywords": list(keywords)},
            )
            insights.append(insight)

        return insights

    def get_insights(self) -> list[Insight]:
        """Get all stored insights."""
        return list(self._insights.values())

    def clear_insights(self) -> int:
        """Clear all insights. Returns count cleared."""
        count = len(self._insights)
        self._insights.clear()
        return count

    def stats(self) -> dict[str, Any]:
        """Get reflection engine statistics."""
        insights = list(self._insights.values())
        type_counts = Counter(i.insight_type for i in insights)

        return {
            "total_insights": len(insights),
            "by_type": dict(type_counts),
            "avg_confidence": round(
                sum(i.confidence for i in insights) / max(len(insights), 1), 3
            ),
        }

    # -----------------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Save insights to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "insights": [
                {
                    "id": i.id,
                    "summary": i.summary,
                    "source_ids": i.source_ids,
                    "insight_type": i.insight_type,
                    "confidence": i.confidence,
                    "created_at": i.created_at,
                    "metadata": i.metadata,
                }
                for i in self._insights.values()
            ]
        }

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> ReflectionEngine:
        """Load insights from JSON file."""
        path = Path(path)
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())
        engine = cls()

        for insight_data in data.get("insights", []):
            insight = Insight(
                id=insight_data["id"],
                summary=insight_data["summary"],
                source_ids=insight_data.get("source_ids", []),
                insight_type=insight_data.get("insight_type", "pattern"),
                confidence=insight_data.get("confidence", 0.5),
                created_at=insight_data.get("created_at", ""),
                metadata=insight_data.get("metadata", {}),
            )
            engine._insights[insight.id] = insight

        return engine
