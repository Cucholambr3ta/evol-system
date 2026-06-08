#!/usr/bin/env python3
"""compat.py — Compatibility Layer for EDMS v1 → v2 Migration.

Provides backward-compatible interface over existing evol_memory_store.py.
New v2 components can be used via this layer without breaking v1.

Usage:
    from evol_memory_v2.compat import MemoryV2
    mem = MemoryV2()
    
    # v1 interface (backward compatible)
    mem.index("text", {"tipo": "decision"})
    results = mem.search("query")
    
    # v2 interface (new features)
    mem.store("verbatim text")  # Verbatim storage
    mem.extract("text")  # Entity extraction
    mem.link("text")  # Auto-linking
"""

import os
import sys
from pathlib import Path
from typing import Any

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from .store import VerbatimStore
from .extractor import EntityExtractor
from .auto_linker import AutoLinker
from .entity_store import EntityStore
from .hybrid_retriever import HybridRetriever, RetrievalResult


class MemoryV2:
    """Unified interface for EDMS v2 with v1 compatibility.

    Wraps v2 components and provides fallback to v1 MemoryStore
    when v2 features are not needed.
    """

    def __init__(self, memory_dir: str | None = None, use_v2: bool = True):
        """Initialize memory system.

        Args:
            memory_dir: Memory directory (default: ~/.evol/memory)
            use_v2: If True, initialize v2 components; if False, use v1 only
        """
        if memory_dir is None:
            memory_dir = os.environ.get(
                "EVOL_MEMORY_DIR", os.path.expanduser("~/.evol/memory")
            )

        self._memory_dir = memory_dir
        self._use_v2 = use_v2 and os.environ.get("EVOL_MEMORY_V2_ENABLED", "1") != "0"

        # v2 components
        if self._use_v2:
            self._verbatim = VerbatimStore(memory_dir)
            self._extractor = EntityExtractor()
            self._linker = AutoLinker(self._extractor)
            self._entity_store = EntityStore(memory_dir)
            self._retriever = HybridRetriever()

        # v1 compatibility
        self._v1_store = None

    def _get_v1_store(self):
        """Lazy-load v1 MemoryStore."""
        if self._v1_store is None:
            try:
                from evol_memory_store import MemoryStore
                self._v1_store = MemoryStore(self._memory_dir)
            except ImportError:
                raise ImportError(
                    "evol_memory_store.py not found. "
                    "Ensure scripts/ is in PYTHONPATH."
                )
        return self._v1_store

    # ── v1 Compatible Interface ─────────────────────────────────────────

    def index(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        """v1 compatible: Index text with metadata.

        In v2, this also:
        1. Stores verbatim text
        2. Extracts entities
        3. Creates auto-links
        """
        # v1 indexing
        v1_result = self._get_v1_store().index(text, metadata)

        if self._use_v2:
            # v2 verbatim storage
            self._verbatim.write(text, metadata)

            # v2 entity extraction
            entities = self._extractor.extract(text)
            for entity in entities:
                self._entity_store.upsert(
                    entity["text"],
                    entity["type"],
                    {"source": "auto_extract", "context": text[:200]},
                    entity.get("confidence", 0.5),
                )

            # v2 auto-linking
            links = self._linker.link(text)
            for link in links:
                self._entity_store.add_relation(
                    link["from_text"],
                    "concept",  # Default type
                    link["to_text"],
                    "concept",
                    link["relation"],
                    {"source": "auto_link", "confidence": link.get("confidence", 0.5)},
                    link.get("confidence", 0.5),
                )

        return v1_result

    def search(
        self,
        query: str,
        limit: int = 10,
        project: str | None = None,
    ) -> list[dict]:
        """v1 compatible: Search memories.

        In v2, results include evidence contracts.
        """
        filters = {}
        if project:
            filters["project"] = project

        # v1 search
        v1_results = self._get_v1_store().search(query, limit=limit, filters=filters)

        if self._use_v2:
            # Enhance with v2 evidence contracts
            for result in v1_results:
                result["evidence"] = {
                    "source": "v1_chromadb",
                    "match_type": "vector_semantic",
                    "confidence": 0.8,
                }

                # Add entity context
                text = result.get("text", "")
                entities = self._extractor.extract(text)
                if entities:
                    result["evidence"]["entities"] = [
                        e["text"] for e in entities
                    ]

        return v1_results

    # ── v2 New Interface ────────────────────────────────────────────────

    def store(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """v2: Store verbatim text (no LLM transformation).

        Returns:
            Item ID
        """
        if not self._use_v2:
            raise RuntimeError("v2 features disabled. Set EVOL_MEMORY_V2_ENABLED=1")

        return self._verbatim.write(text, metadata)

    def read(self, item_id: str) -> dict | None:
        """v2: Read verbatim item by ID."""
        if not self._use_v2:
            raise RuntimeError("v2 features disabled")

        return self._verbatim.read(item_id)

    def extract(self, text: str) -> dict[str, Any]:
        """v2: Extract entities and relationships from text.

        Returns:
            Dict with 'entities' and 'relationships' lists
        """
        if not self._use_v2:
            raise RuntimeError("v2 features disabled")

        return self._extractor.extract_all(text)

    def link(self, text: str) -> list[dict[str, Any]]:
        """v2: Create auto-links from text.

        Returns:
            List of link dicts
        """
        if not self._use_v2:
            raise RuntimeError("v2 features disabled")

        return self._linker.link(text)

    def get_entity(self, name: str, entity_type: str | None = None) -> dict | None:
        """v2: Get entity by name."""
        if not self._use_v2:
            raise RuntimeError("v2 features disabled")

        return self._entity_store.get(name, entity_type)

    def get_entity_relations(self, entity_name: str) -> list[dict]:
        """v2: Get relationships for entity."""
        if not self._use_v2:
            raise RuntimeError("v2 features disabled")

        return self._entity_store.get_relations(entity_name=entity_name)

    def verify_integrity(self, item_id: str) -> dict:
        """v2: Verify item integrity via content hash."""
        if not self._use_v2:
            raise RuntimeError("v2 features disabled")

        return self._verbatim.verify_integrity(item_id)

    def stats(self) -> dict:
        """v2: Get combined statistics."""
        result = {}

        if self._use_v2:
            result["v2"] = {
                "verbatim": self._verbatim.stats(),
                "entities": self._entity_store.stats(),
                "retriever": self._retriever.stats(),
            }

        result["v1"] = {"status": "available" if self._v1_store else "not_loaded"}

        return result

    # ── Hybrid Retrieval ────────────────────────────────────────────────

    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        include_evidence: bool = True,
    ) -> list[RetrievalResult]:
        """v2: Hybrid search using vector + BM25 + graph.

        Args:
            query: Search query
            top_k: Maximum results
            include_evidence: Include evidence contracts

        Returns:
            List of RetrievalResult with fused scores
        """
        if not self._use_v2:
            raise RuntimeError("v2 features disabled")

        return self._retriever.search(query, top_k, include_evidence=include_evidence)

    def add_to_retriever(
        self,
        doc_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """v2: Add document to hybrid retriever.

        Args:
            doc_id: Document ID
            text: Document text
            metadata: Optional metadata
        """
        if not self._use_v2:
            raise RuntimeError("v2 features disabled")

        self._retriever.add_document(doc_id, text, metadata)
