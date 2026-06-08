#!/usr/bin/env python3
"""store.py — Verbatim Storage for Evol-DD Memory v2.0.

Stores original text without LLM transformation. Every item includes:
- SHA-256 content hash for integrity verification
- Verbatim text (never summarized)
- Metadata with timestamps
- Optional embedding (regenerable, not primary)

Inspired by MemPalace's verbatim principle:
"Never summarize, paraphrase, or lossy-compress user data."

Usage:
    from evol_memory_v2.store import VerbatimStore
    store = VerbatimStore()
    item_id = store.write("Decidimos usar ChromaDB", {"tipo": "decision"})
    item = store.read(item_id)
    assert item["verbatim"] == "Decidimos usar ChromaDB"
"""

import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any


def _content_hash(text: str) -> str:
    """SHA-256 hash of content for integrity verification."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _make_id(text: str, prefix: str = "mem") -> str:
    """Deterministic ID from content hash."""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{h}"


class VerbatimStore:
    """Append-only verbatim memory store with integrity verification.

    Stores original text, never summarizes. Embeddings and summaries
    are generated as separate cache, never as replacement.

    ADR-001: Almacenamiento Verbatim como Principio Fundacional.
    """

    def __init__(self, memory_dir: str | None = None):
        if memory_dir is None:
            memory_dir = os.environ.get(
                "EVOL_MEMORY_DIR", os.path.expanduser("~/.evol/memory")
            )
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self._store_file = self.memory_dir / "verbatim_store.json"
        self._index_file = self.memory_dir / "verbatim_index.json"
        self._store: dict[str, dict] = {}
        self._index: dict[str, str] = {}  # hash -> id (dedup)
        self._load()

    def _load(self):
        """Load store from disk."""
        if self._store_file.exists():
            with open(self._store_file) as f:
                self._store = json.load(f)
        if self._index_file.exists():
            with open(self._index_file) as f:
                self._index = json.load(f)

    def _save(self):
        """Persist store to disk."""
        with open(self._store_file, "w") as f:
            json.dump(self._store, f, indent=2, ensure_ascii=False)
        with open(self._index_file, "w") as f:
            json.dump(self._index, f, indent=2, ensure_ascii=False)

    def write(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        prefix: str = "mem",
    ) -> str:
        """Store verbatim text with metadata.

        Args:
            text: Original text (never transformed)
            metadata: Optional metadata dict
            prefix: ID prefix (default: "mem")

        Returns:
            Item ID

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        text = text.strip()
        content = _content_hash(text)

        # Dedup by content hash
        if content in self._index:
            return self._index[content]

        item_id = _make_id(text, prefix)
        now = datetime.now().isoformat()

        item = {
            "id": item_id,
            "verbatim": text,
            "content_hash": content,
            "metadata": metadata or {},
            "created_at": now,
            "updated_at": now,
            "version": 1,
            "is_latest": True,
        }

        self._store[item_id] = item
        self._index[content] = item_id
        self._save()

        return item_id

    def read(self, item_id: str) -> dict | None:
        """Read item by ID.

        Returns:
            Item dict with verbatim text and metadata, or None if not found
        """
        return self._store.get(item_id)

    def read_by_hash(self, content_hash: str) -> dict | None:
        """Read item by content hash.

        Returns:
            Item dict or None
        """
        item_id = self._index.get(content_hash)
        if item_id:
            return self._store.get(item_id)
        return None

    def update(
        self, item_id: str, text: str, metadata: dict[str, Any] | None = None
    ) -> bool:
        """Update item (creates new version, preserves history).

        Args:
            item_id: Item to update
            text: New verbatim text
            metadata: Optional new metadata (merged with existing)

        Returns:
            True if updated, False if not found
        """
        if item_id not in self._store:
            return False

        old_item = self._store[item_id]
        old_item["is_latest"] = False
        old_item["updated_at"] = datetime.now().isoformat()

        # Create new version
        new_text = text.strip()
        new_id = _make_id(new_text, prefix=item_id.split("_")[0])
        new_content = _content_hash(new_text)

        merged_metadata = {**old_item.get("metadata", {})}
        if metadata:
            merged_metadata.update(metadata)

        new_item = {
            "id": new_id,
            "verbatim": new_text,
            "content_hash": new_content,
            "metadata": merged_metadata,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": old_item.get("version", 1) + 1,
            "is_latest": True,
            "previous_version": item_id,
        }

        self._store[new_id] = new_item
        self._index[new_content] = new_id
        self._save()

        return True

    def delete(self, item_id: str, soft: bool = True) -> bool:
        """Delete item (soft by default).

        Args:
            item_id: Item to delete
            soft: If True, mark as deleted; if False, remove entirely

        Returns:
            True if deleted, False if not found
        """
        if item_id not in self._store:
            return False

        if soft:
            self._store[item_id]["is_latest"] = False
            self._store[item_id]["deleted_at"] = datetime.now().isoformat()
            self._store[item_id]["updated_at"] = datetime.now().isoformat()
        else:
            item = self._store.pop(item_id)
            content_hash = item.get("content_hash")
            if content_hash and self._index.get(content_hash) == item_id:
                del self._index[content_hash]

        self._save()
        return True

    def search(
        self,
        query: str,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict]:
        """Search items by text similarity (simple substring match).

        For semantic search, use evol_memory_store.py's MemoryStore.

        Args:
            query: Search query
            limit: Max results
            filters: Metadata filters (key=value)

        Returns:
            List of matching items with scores
        """
        query_lower = query.lower()
        results = []

        for item_id, item in self._store.items():
            if not item.get("is_latest", True):
                continue

            verbatim = item.get("verbatim", "").lower()

            # Simple substring match scoring
            score = 0.0
            if query_lower in verbatim:
                score = 1.0
            else:
                # Word-level matching
                query_words = query_lower.split()
                matched = sum(1 for w in query_words if w in verbatim)
                if query_words:
                    score = matched / len(query_words)

            if score <= 0:
                continue

            # Apply metadata filters
            if filters:
                meta = item.get("metadata", {})
                if not all(meta.get(k) == v for k, v in filters.items()):
                    continue

            results.append({
                "id": item_id,
                "verbatim": item["verbatim"],
                "score": score,
                "metadata": item.get("metadata", {}),
                "created_at": item.get("created_at"),
                "content_hash": item.get("content_hash"),
            })

        results.sort(key=lambda x: -x["score"])
        return results[:limit]

    def list_items(
        self,
        limit: int = 100,
        offset: int = 0,
        only_latest: bool = True,
    ) -> list[dict]:
        """List items with pagination.

        Args:
            limit: Max results
            offset: Skip N items
            only_latest: If True, only return latest versions

        Returns:
            List of items
        """
        items = []
        for item in self._store.values():
            if only_latest and not item.get("is_latest", True):
                continue
            items.append(item)

        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[offset : offset + limit]

    def verify_integrity(self, item_id: str) -> dict:
        """Verify item integrity via content hash.

        Returns:
            Dict with valid: bool, expected: str, actual: str
        """
        item = self._store.get(item_id)
        if not item:
            return {"valid": False, "error": "Item not found"}

        expected = item.get("content_hash", "")
        actual = _content_hash(item.get("verbatim", ""))

        return {
            "valid": expected == actual,
            "expected": expected,
            "actual": actual,
            "item_id": item_id,
        }

    def stats(self) -> dict:
        """Get store statistics."""
        total = len(self._store)
        latest = sum(1 for i in self._store.values() if i.get("is_latest", True))
        deleted = sum(1 for i in self._store.values() if "deleted_at" in i)

        total_chars = sum(
            len(i.get("verbatim", "")) for i in self._store.values()
            if i.get("is_latest", True)
        )

        return {
            "total_items": total,
            "latest_items": latest,
            "deleted_items": deleted,
            "total_characters": total_chars,
            "estimated_tokens": total_chars // 4,
            "store_file": str(self._store_file),
        }
