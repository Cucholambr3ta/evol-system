#!/usr/bin/env python3
"""entity_store.py — Centralized Entity Storage for Evol-DD Memory v2.0.

Stores entities with temporal validity windows and merge-by-threshold.
Supports versioned entities with isLatest flag.

Inspired by MemPalace's temporal KG and Mem0's entity store pattern.

Usage:
    from evol_memory_v2.entity_store import EntityStore
    store = EntityStore()
    store.upsert("ChromaDB", "technology", {"description": "Vector database"})
    store.upsert("ChromaDB", "technology", {"description": "Vector DB for EDMS"})
    entity = store.get("ChromaDB")
    assert entity["version"] == 2
    assert entity["is_latest"] == True
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def _entity_id(name: str, etype: str, version: int = 1) -> str:
    """Deterministic entity ID from name, type, and version."""
    key = f"{name.lower()}:{etype}:v{version}"
    return hashlib.sha256(key.encode()).hexdigest()[:12]


class EntityStore:
    """Centralized entity storage with temporal validity.

    Entities are versioned with isLatest flag. Temporal queries
    supported via valid_from/valid_to windows.

    ADR-007: Entity Store con Ventanas de Validez Temporales.
    """

    def __init__(self, memory_dir: str | None = None):
        if memory_dir is None:
            memory_dir = os.environ.get(
                "EVOL_MEMORY_DIR", os.path.expanduser("~/.evol/memory")
            )
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self._entities_file = self.memory_dir / "entities.json"
        self._relations_file = self.memory_dir / "entity_relations.json"
        self._entities: dict[str, dict] = {}
        self._relations: list[dict] = []
        self._load()

    def _load(self):
        """Load from disk."""
        if self._entities_file.exists():
            with open(self._entities_file) as f:
                self._entities = json.load(f)
        if self._relations_file.exists():
            with open(self._relations_file) as f:
                self._relations = json.load(f)

    def _save(self):
        """Persist to disk."""
        with open(self._entities_file, "w") as f:
            json.dump(self._entities, f, indent=2, ensure_ascii=False)
        with open(self._relations_file, "w") as f:
            json.dump(self._relations, f, indent=2, ensure_ascii=False)

    def upsert(
        self,
        name: str,
        entity_type: str,
        properties: dict[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> str:
        """Insert or update entity.

        If entity exists with same name+type, creates new version.
        Old version gets isLatest=false.

        Args:
            name: Entity name
            entity_type: Entity type (technology, project, concept, etc.)
            properties: Optional properties dict
            confidence: Confidence score (0.0-1.0)

        Returns:
            Entity ID
        """
        now = datetime.now().isoformat()

        # Find existing entity with same name+type
        existing = None
        for e in self._entities.values():
            if (
                e.get("name", "").lower() == name.lower()
                and e.get("type") == entity_type
                and e.get("is_latest", False)
            ):
                existing = e
                break

        if existing:
            # Mark old version as not latest
            existing["is_latest"] = False
            existing["updated_at"] = now

            # Create new version
            new_version = existing.get("version", 1) + 1
            merged_props = {**existing.get("properties", {})}
            if properties:
                merged_props.update(properties)

            entity_id = _entity_id(name, entity_type, new_version)
            entity = {
                "id": entity_id,
                "name": name,
                "type": entity_type,
                "properties": merged_props,
                "confidence": confidence,
                "version": new_version,
                "is_latest": True,
                "created_at": existing.get("created_at", now),
                "updated_at": now,
                "valid_from": now,
                "valid_to": None,
                "previous_version": existing.get("id"),
            }
        else:
            # New entity
            entity_id = _entity_id(name, entity_type, 1)
            entity = {
                "id": entity_id,
                "name": name,
                "type": entity_type,
                "properties": properties or {},
                "confidence": confidence,
                "version": 1,
                "is_latest": True,
                "created_at": now,
                "updated_at": now,
                "valid_from": now,
                "valid_to": None,
                "previous_version": None,
            }

        self._entities[entity_id] = entity
        self._save()

        return entity_id

    def get(self, name: str, entity_type: str | None = None) -> dict | None:
        """Get latest entity by name.

        Args:
            name: Entity name
            entity_type: Optional type filter

        Returns:
            Entity dict or None
        """
        name_lower = name.lower()
        for entity in self._entities.values():
            if (
                entity.get("name", "").lower() == name_lower
                and entity.get("is_latest", False)
            ):
                if entity_type and entity.get("type") != entity_type:
                    continue
                return entity
        return None

    def get_by_id(self, entity_id: str) -> dict | None:
        """Get entity by ID."""
        return self._entities.get(entity_id)

    def get_all(
        self,
        entity_type: str | None = None,
        only_latest: bool = True,
    ) -> list[dict]:
        """Get all entities.

        Args:
            entity_type: Optional type filter
            only_latest: If True, only return latest versions

        Returns:
            List of entities
        """
        results = []
        for entity in self._entities.values():
            if only_latest and not entity.get("is_latest", False):
                continue
            if entity_type and entity.get("type") != entity_type:
                continue
            results.append(entity)
        return results

    def invalidate(
        self, name: str, entity_type: str, ended: str | None = None
    ) -> bool:
        """Mark entity as no longer valid.

        Args:
            name: Entity name
            entity_type: Entity type
            ended: End date (ISO format, default: now)

        Returns:
            True if invalidated, False if not found
        """
        entity = self.get(name, entity_type)
        if not entity:
            return False

        ended = ended or datetime.now().isoformat()
        entity["valid_to"] = ended
        entity["is_latest"] = False
        entity["updated_at"] = ended

        self._save()
        return True

    def add_relation(
        self,
        from_name: str,
        from_type: str,
        to_name: str,
        to_type: str,
        relation: str,
        metadata: dict[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> int:
        """Add relationship between entities.

        Args:
            from_name: Source entity name
            from_type: Source entity type
            to_name: Target entity name
            to_type: Target entity type
            relation: Relationship type
            metadata: Optional metadata
            confidence: Confidence score

        Returns:
            Relation index
        """
        from_id = _entity_id(from_name, from_type)
        to_id = _entity_id(to_name, to_type)
        now = datetime.now().isoformat()

        relation_data = {
            "from_id": from_id,
            "from_name": from_name,
            "to_id": to_id,
            "to_name": to_name,
            "relation": relation,
            "metadata": metadata or {},
            "confidence": confidence,
            "created_at": now,
            "is_valid": True,
        }

        self._relations.append(relation_data)
        self._save()

        return len(self._relations) - 1

    def get_relations(
        self,
        entity_name: str | None = None,
        relation_type: str | None = None,
        only_valid: bool = True,
    ) -> list[dict]:
        """Get relationships.

        Args:
            entity_name: Filter by entity name (either source or target)
            relation_type: Filter by relationship type
            only_valid: If True, only return valid relations

        Returns:
            List of relations
        """
        results = []
        for rel in self._relations:
            if only_valid and not rel.get("is_valid", True):
                continue
            if relation_type and rel.get("relation") != relation_type:
                continue
            if entity_name:
                name_lower = entity_name.lower()
                if (
                    rel.get("from_name", "").lower() != name_lower
                    and rel.get("to_name", "").lower() != name_lower
                ):
                    continue
            results.append(rel)
        return results

    def search(
        self,
        query: str,
        limit: int = 10,
        entity_type: str | None = None,
    ) -> list[dict]:
        """Search entities by name similarity.

        Args:
            query: Search query
            limit: Max results
            entity_type: Optional type filter

        Returns:
            List of matching entities with scores
        """
        query_lower = query.lower()
        results = []

        for entity in self._entities.values():
            if not entity.get("is_latest", False):
                continue
            if entity_type and entity.get("type") != entity_type:
                continue

            name = entity.get("name", "").lower()
            score = 0.0

            if query_lower in name:
                score = 1.0
            else:
                query_words = query_lower.split()
                matched = sum(1 for w in query_words if w in name)
                if query_words:
                    score = matched / len(query_words)

            if score <= 0:
                continue

            results.append({
                "id": entity["id"],
                "name": entity["name"],
                "type": entity.get("type"),
                "score": score,
                "confidence": entity.get("confidence"),
                "version": entity.get("version"),
            })

        results.sort(key=lambda x: -x["score"])
        return results[:limit]

    def stats(self) -> dict:
        """Get store statistics."""
        total = len(self._entities)
        latest = sum(1 for e in self._entities.values() if e.get("is_latest", False))
        types = {}
        for e in self._entities.values():
            if e.get("is_latest", False):
                t = e.get("type", "unknown")
                types[t] = types.get(t, 0) + 1

        return {
            "total_entities": total,
            "latest_entities": latest,
            "total_relations": len(self._relations),
            "valid_relations": sum(
                1 for r in self._relations if r.get("is_valid", True)
            ),
            "entity_types": types,
        }
