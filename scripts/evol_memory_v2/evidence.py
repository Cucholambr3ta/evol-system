"""
Evidence contracts for EDMS Memory v2.0.

Provides structured metadata for each retrieval result,
including source, confidence, temporal validity, and relationships.

Part of EDMS Memory v2.0 Phase 2 - Hybrid Retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class EvidenceSource:
    """Source information for an evidence item."""
    type: str  # "verbatim", "summary", "derived", "inferred"
    id: str    # Source document/item ID
    confidence: float = 1.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "id": self.id,
            "confidence": round(self.confidence, 3),
            "timestamp": self.timestamp,
        }


@dataclass
class EvidenceRelationship:
    """Relationship between evidence items."""
    source_id: str
    target_id: str
    relation: str  # "DERIVED_FROM", "CONTRADICTS", "SUPPORTS", "REFERENCES"
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "relation": self.relation,
            "confidence": round(self.confidence, 3),
        }


@dataclass
class EvidenceTemporal:
    """Temporal validity information."""
    valid_from: str = ""
    valid_to: str = ""
    confidence: float = 1.0
    is_current: bool = True

    def __post_init__(self):
        if not self.valid_from:
            self.valid_from = datetime.now().isoformat()

    def is_valid_at(self, timestamp: str | None = None) -> bool:
        """Check if evidence is valid at given timestamp."""
        if timestamp is None:
            return self.is_current

        if self.valid_to and timestamp > self.valid_to:
            return False
        if timestamp < self.valid_from:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "confidence": round(self.confidence, 3),
            "is_current": self.is_current,
        }


@dataclass
class EvidenceContract:
    """
    Complete evidence contract for a retrieval result.

    Provides structured metadata explaining why a result is relevant,
    where it came from, and its temporal validity.

    Usage:
        contract = EvidenceContract(
            item_id="doc-123",
            sources=[EvidenceSource("verbatim", "session-456")],
            temporal=EvidenceTemporal(),
            reasoning="Matched on ChromaDB keyword",
            relationships=[],
        )
        # Attach to search result
        result["evidence"] = contract.to_dict()
    """
    item_id: str
    sources: list[EvidenceSource] = field(default_factory=list)
    temporal: EvidenceTemporal = field(default_factory=EvidenceTemporal)
    relationships: list[EvidenceRelationship] = field(default_factory=list)
    reasoning: str = ""
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_source(
        self,
        source_type: str,
        source_id: str,
        confidence: float = 1.0,
    ) -> None:
        """Add a source to the evidence."""
        self.sources.append(EvidenceSource(source_type, source_id, confidence))

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relation: str,
        confidence: float = 1.0,
    ) -> None:
        """Add a relationship to the evidence."""
        self.relationships.append(EvidenceRelationship(
            source_id, target_id, relation, confidence
        ))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "item_id": self.item_id,
            "sources": [s.to_dict() for s in self.sources],
            "temporal": self.temporal.to_dict(),
            "relationships": [r.to_dict() for r in self.relationships],
            "reasoning": self.reasoning,
            "confidence": round(self.confidence, 3),
            "metadata": self.metadata,
        }


class EvidenceBuilder:
    """
    Builder for creating evidence contracts.

    Usage:
        builder = EvidenceBuilder()
        contract = (
            builder
            .for_item("doc-123")
            .with_source("verbatim", "session-456", confidence=0.9)
            .with_reasoning("Matched on ChromaDB keyword")
            .with_temporal(valid_from="2026-01-01", valid_to="2026-12-31")
            .with_confidence(0.85)
            .build()
        )
    """

    def __init__(self):
        self._item_id: str = ""
        self._sources: list[EvidenceSource] = []
        self._temporal: EvidenceTemporal = field(default_factory=EvidenceTemporal)
        self._relationships: list[EvidenceRelationship] = []
        self._reasoning: str = ""
        self._confidence: float = 1.0
        self._metadata: dict[str, Any] = {}

    def for_item(self, item_id: str) -> EvidenceBuilder:
        """Set the item ID."""
        self._item_id = item_id
        return self

    def with_source(
        self,
        source_type: str,
        source_id: str,
        confidence: float = 1.0,
    ) -> EvidenceBuilder:
        """Add a source."""
        self._sources.append(EvidenceSource(source_type, source_id, confidence))
        return self

    def with_temporal(
        self,
        valid_from: str = "",
        valid_to: str = "",
        confidence: float = 1.0,
        is_current: bool = True,
    ) -> EvidenceBuilder:
        """Set temporal validity."""
        self._temporal = EvidenceTemporal(valid_from, valid_to, confidence, is_current)
        return self

    def with_relationship(
        self,
        source_id: str,
        target_id: str,
        relation: str,
        confidence: float = 1.0,
    ) -> EvidenceBuilder:
        """Add a relationship."""
        self._relationships.append(EvidenceRelationship(
            source_id, target_id, relation, confidence
        ))
        return self

    def with_reasoning(self, reasoning: str) -> EvidenceBuilder:
        """Set reasoning text."""
        self._reasoning = reasoning
        return self

    def with_confidence(self, confidence: float) -> EvidenceBuilder:
        """Set overall confidence."""
        self._confidence = confidence
        return self

    def with_metadata(self, key: str, value: Any) -> EvidenceBuilder:
        """Add metadata key-value pair."""
        self._metadata[key] = value
        return self

    def build(self) -> EvidenceContract:
        """Build the evidence contract."""
        if not self._item_id:
            raise ValueError("item_id is required")

        return EvidenceContract(
            item_id=self._item_id,
            sources=self._sources,
            temporal=self._temporal,
            relationships=self._relationships,
            reasoning=self._reasoning,
            confidence=self._confidence,
            metadata=self._metadata,
        )


def create_evidence_from_result(
    result: dict[str, Any],
    source_type: str = "verbatim",
    source_id: str = "",
) -> EvidenceContract:
    """
    Create an evidence contract from a search result.

    Args:
        result: Search result dict with id, score, text, metadata
        source_type: Type of source (verbatim, summary, etc.)
        source_id: Source identifier

    Returns:
        EvidenceContract with appropriate metadata
    """
    builder = EvidenceBuilder()

    contract = (
        builder
        .for_item(result.get("id", ""))
        .with_source(source_type, source_id or result.get("id", ""))
        .with_reasoning(f"Score: {result.get('score', 0):.3f}")
        .with_confidence(result.get("score", 0.5))
        .build()
    )

    # Add metadata from result
    metadata = result.get("metadata", {})
    if "tier" in metadata:
        contract.metadata["tier"] = metadata["tier"]
    if "tipo" in metadata:
        contract.metadata["tipo"] = metadata["tipo"]
    if "importance" in metadata:
        contract.metadata["importance"] = metadata["importance"]

    return contract
