"""
Agent File format for EDMS Memory v2.0.

Portable format for agent memory, inspired by Letta.
Provides immutable snapshots of agent memory for portability.

Part of EDMS Memory v2.0 Phase 4 - Portability and Ecosystem.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class AgentMemorySnapshot:
    """Immutable snapshot of agent memory."""
    agent_id: str
    agent_name: str
    created_at: str
    version: str = "1.0.0"
    memory_items: list[dict[str, Any]] = field(default_factory=list)
    entities: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    insights: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.checksum:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate SHA-256 checksum of snapshot content."""
        content = json.dumps({
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "created_at": self.created_at,
            "version": self.version,
            "memory_items": self.memory_items,
            "entities": self.entities,
            "relationships": self.relationships,
            "insights": self.insights,
            "metadata": self.metadata,
        }, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_integrity(self) -> dict[str, Any]:
        """
        Verify snapshot integrity via checksum.

        Returns:
            Dict with is_valid flag and expected/found checksums
        """
        expected = self._calculate_checksum()
        is_valid = expected == self.checksum
        return {
            "is_valid": is_valid,
            "expected_checksum": expected,
            "found_checksum": self.checksum,
        }


class AgentFile:
    """
    Agent File format for portable agent memory.

    Creates immutable snapshots of agent memory that can be
    transferred between systems or stored for archival.

    Usage:
        agent_file = AgentFile()
        snapshot = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent",
            memories=[...],
            entities=[...],
        )
        agent_file.save(snapshot, "agent_evol-builder.json")

        # Load in another system
        loaded = agent_file.load("agent_evol-builder.json")
    """

    def __init__(self):
        self._format_version = "1.0.0"

    def create_snapshot(
        self,
        agent_id: str,
        agent_name: str,
        memories: list[dict[str, Any]] | None = None,
        entities: list[dict[str, Any]] | None = None,
        relationships: list[dict[str, Any]] | None = None,
        insights: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentMemorySnapshot:
        """
        Create an immutable snapshot of agent memory.

        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            memories: List of memory items
            entities: List of entities
            relationships: List of relationships
            insights: List of insights
            metadata: Additional metadata

        Returns:
            AgentMemorySnapshot with calculated checksum
        """
        snapshot = AgentMemorySnapshot(
            agent_id=agent_id,
            agent_name=agent_name,
            created_at=datetime.now().isoformat(),
            version=self._format_version,
            memory_items=memories or [],
            entities=entities or [],
            relationships=relationships or [],
            insights=insights or [],
            metadata=metadata or {},
        )
        # Calculate checksum after all data is set
        snapshot.checksum = snapshot._calculate_checksum()
        return snapshot

    def save(
        self,
        snapshot: AgentMemorySnapshot,
        path: str | Path,
    ) -> dict[str, Any]:
        """
        Save snapshot to JSON file.

        Args:
            snapshot: AgentMemorySnapshot to save
            path: Output file path

        Returns:
            Dict with save metadata (path, size, checksum)
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "format_version": snapshot.version,
            "agent_id": snapshot.agent_id,
            "agent_name": snapshot.agent_name,
            "created_at": snapshot.created_at,
            "checksum": snapshot.checksum,
            "memory_items": snapshot.memory_items,
            "entities": snapshot.entities,
            "relationships": snapshot.relationships,
            "insights": snapshot.insights,
            "metadata": snapshot.metadata,
        }

        content = json.dumps(data, ensure_ascii=False, indent=2)
        path.write_text(content)

        return {
            "path": str(path),
            "size_bytes": len(content.encode()),
            "checksum": snapshot.checksum,
            "items_count": {
                "memories": len(snapshot.memory_items),
                "entities": len(snapshot.entities),
                "relationships": len(snapshot.relationships),
                "insights": len(snapshot.insights),
            },
        }

    def load(self, path: str | Path) -> AgentMemorySnapshot:
        """
        Load snapshot from JSON file.

        Args:
            path: Input file path

        Returns:
            AgentMemorySnapshot

        Raises:
            ValueError: If checksum verification fails
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Agent file not found: {path}")

        data = json.loads(path.read_text())

        snapshot = AgentMemorySnapshot(
            agent_id=data["agent_id"],
            agent_name=data["agent_name"],
            created_at=data["created_at"],
            version=data.get("format_version", "1.0.0"),
            memory_items=data.get("memory_items", []),
            entities=data.get("entities", []),
            relationships=data.get("relationships", []),
            insights=data.get("insights", []),
            metadata=data.get("metadata", {}),
            checksum=data.get("checksum", ""),
        )

        # Verify integrity
        verification = snapshot.verify_integrity()
        if not verification["is_valid"]:
            raise ValueError(
                f"Checksum mismatch: expected {verification['expected_checksum']}, "
                f"found {verification['found_checksum']}"
            )

        return snapshot

    def merge(
        self,
        snapshot1: AgentMemorySnapshot,
        snapshot2: AgentMemorySnapshot,
    ) -> AgentMemorySnapshot:
        """
        Merge two snapshots from the same agent.

        Args:
            snapshot1: First snapshot (older)
            snapshot2: Second snapshot (newer)

        Returns:
            Merged AgentMemorySnapshot
        """
        if snapshot1.agent_id != snapshot2.agent_id:
            raise ValueError("Cannot merge snapshots from different agents")

        # Merge memory items (deduplicate by content hash)
        seen_hashes: set[str] = set()
        merged_memories: list[dict[str, Any]] = []

        for mem in snapshot1.memory_items + snapshot2.memory_items:
            content = json.dumps(mem, sort_keys=True, ensure_ascii=False)
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                merged_memories.append(mem)

        # Merge entities (keep latest version)
        entity_map: dict[str, dict[str, Any]] = {}
        for entity in snapshot1.entities + snapshot2.entities:
            key = f"{entity.get('name', '')}:{entity.get('type', '')}"
            if key not in entity_map or entity.get("version", 0) > entity_map[key].get("version", 0):
                entity_map[key] = entity

        # Merge relationships (deduplicate)
        seen_rels: set[str] = set()
        merged_rels: list[dict[str, Any]] = []

        for rel in snapshot1.relationships + snapshot2.relationships:
            rel_key = f"{rel.get('source', '')}:{rel.get('relation', '')}:{rel.get('target', '')}"
            if rel_key not in seen_rels:
                seen_rels.add(rel_key)
                merged_rels.append(rel)

        # Merge insights (keep all, they might be different)
        merged_insights = snapshot1.insights + snapshot2.insights

        # Create merged snapshot
        merged = self.create_snapshot(
            agent_id=snapshot1.agent_id,
            agent_name=snapshot2.agent_name,  # Use newer name
            memories=merged_memories,
            entities=list(entity_map.values()),
            relationships=merged_rels,
            insights=merged_insights,
            metadata={
                "merged_from": [snapshot1.created_at, snapshot2.created_at],
                "merge_timestamp": datetime.now().isoformat(),
            },
        )

        return merged

    def diff(
        self,
        snapshot1: AgentMemorySnapshot,
        snapshot2: AgentMemorySnapshot,
    ) -> dict[str, Any]:
        """
        Compare two snapshots and show differences.

        Args:
            snapshot1: First snapshot
            snapshot2: Second snapshot

        Returns:
            Dict with differences
        """
        # Compare memory counts
        mem_diff = len(snapshot2.memory_items) - len(snapshot1.memory_items)
        entity_diff = len(snapshot2.entities) - len(snapshot1.entities)
        rel_diff = len(snapshot2.relationships) - len(snapshot1.relationships)
        insight_diff = len(snapshot2.insights) - len(snapshot1.insights)

        return {
            "agent_id": snapshot1.agent_id,
            "snapshot1_created": snapshot1.created_at,
            "snapshot2_created": snapshot2.created_at,
            "differences": {
                "memories": {
                    "count_change": mem_diff,
                    "snapshot1_count": len(snapshot1.memory_items),
                    "snapshot2_count": len(snapshot2.memory_items),
                },
                "entities": {
                    "count_change": entity_diff,
                    "snapshot1_count": len(snapshot1.entities),
                    "snapshot2_count": len(snapshot2.entities),
                },
                "relationships": {
                    "count_change": rel_diff,
                    "snapshot1_count": len(snapshot1.relationships),
                    "snapshot2_count": len(snapshot2.relationships),
                },
                "insights": {
                    "count_change": insight_diff,
                    "snapshot1_count": len(snapshot1.insights),
                    "snapshot2_count": len(snapshot2.insights),
                },
            },
            "checksum1": snapshot1.checksum,
            "checksum2": snapshot2.checksum,
            "identical": snapshot1.checksum == snapshot2.checksum,
        }

    def stats(self, snapshot: AgentMemorySnapshot) -> dict[str, Any]:
        """Get snapshot statistics."""
        return {
            "agent_id": snapshot.agent_id,
            "agent_name": snapshot.agent_name,
            "created_at": snapshot.created_at,
            "version": snapshot.version,
            "checksum": snapshot.checksum,
            "counts": {
                "memories": len(snapshot.memory_items),
                "entities": len(snapshot.entities),
                "relationships": len(snapshot.relationships),
                "insights": len(snapshot.insights),
            },
            "total_items": (
                len(snapshot.memory_items)
                + len(snapshot.entities)
                + len(snapshot.relationships)
                + len(snapshot.insights)
            ),
        }
