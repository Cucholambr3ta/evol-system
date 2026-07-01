#!/usr/bin/env python3
"""test_memory_v2.py — Tests for Evol-DD Memory v2.0 Phase 1 Components.

Tests:
- VerbatimStore: write, read, update, delete, search, verify integrity
- EntityExtractor: entity extraction, relationship extraction
- AutoLinker: pattern-based linking, proximity linking
- EntityStore: upsert, get, invalidate, relations
- MemoryV2: v1 compatibility, v2 features

Run: python -m pytest tests/test_memory_v2.py -v
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evol_memory_v2.store import VerbatimStore, _content_hash
from evol_memory_v2.extractor import EntityExtractor
from evol_memory_v2.auto_linker import AutoLinker
from evol_memory_v2.entity_store import EntityStore


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


# ── VerbatimStore Tests ───────────────────────────────────────────────────

class TestVerbatimStore:
    """Tests for VerbatimStore."""

    def test_write_and_read(self, temp_dir):
        """Test basic write and read."""
        store = VerbatimStore(temp_dir)
        text = "Decidimos usar ChromaDB para vector search"
        item_id = store.write(text, {"tipo": "decision"})

        assert item_id is not None
        assert item_id.startswith("mem_")

        item = store.read(item_id)
        assert item is not None
        assert item["verbatim"] == text
        assert item["metadata"]["tipo"] == "decision"
        assert item["is_latest"] is True
        assert item["version"] == 1

    def test_content_hash_deterministic(self):
        """Test content hash is deterministic."""
        text = "Test content"
        h1 = _content_hash(text)
        h2 = _content_hash(text)
        assert h1 == h2
        assert len(h1) == 16

    def test_content_hash_different(self):
        """Test different texts produce different hashes."""
        h1 = _content_hash("Text A")
        h2 = _content_hash("Text B")
        assert h1 != h2

    def test_dedup_by_content(self, temp_dir):
        """Test duplicate content is deduplicated."""
        store = VerbatimStore(temp_dir)
        text = "Same content"
        id1 = store.write(text)
        id2 = store.write(text)
        assert id1 == id2  # Same ID returned

    def test_update_creates_version(self, temp_dir):
        """Test update creates new version."""
        store = VerbatimStore(temp_dir)
        text1 = "Original text"
        text2 = "Updated text"

        id1 = store.write(text1)
        store.update(id1, text2)

        item = store.read(id1)
        assert item["is_latest"] is False

        # New version should exist
        items = store.list_items()
        latest = [i for i in items if i["is_latest"]]
        assert len(latest) == 1
        assert latest[0]["verbatim"] == text2
        assert latest[0]["version"] == 2

    def test_soft_delete(self, temp_dir):
        """Test soft delete."""
        store = VerbatimStore(temp_dir)
        item_id = store.write("To be deleted")
        assert store.delete(item_id, soft=True) is True

        item = store.read(item_id)
        assert item["is_latest"] is False
        assert "deleted_at" in item

    def test_hard_delete(self, temp_dir):
        """Test hard delete."""
        store = VerbatimStore(temp_dir)
        item_id = store.write("To be removed")
        assert store.delete(item_id, soft=False) is True

        item = store.read(item_id)
        assert item is None

    def test_search(self, temp_dir):
        """Test search functionality."""
        store = VerbatimStore(temp_dir)
        store.write("ChromaDB para vector search")
        store.write("LadybugDB para graph database")
        store.write("Nothing related")

        results = store.search("ChromaDB")
        assert len(results) > 0
        assert "ChromaDB" in results[0]["verbatim"]

    def test_verify_integrity(self, temp_dir):
        """Test integrity verification."""
        store = VerbatimStore(temp_dir)
        item_id = store.write("Integrity test")

        result = store.verify_integrity(item_id)
        assert result["valid"] is True

    def test_empty_text_raises(self, temp_dir):
        """Test empty text raises ValueError."""
        store = VerbatimStore(temp_dir)
        with pytest.raises(ValueError):
            store.write("")

    def test_stats(self, temp_dir):
        """Test stats function."""
        store = VerbatimStore(temp_dir)
        store.write("Item 1")
        store.write("Item 2")

        stats = store.stats()
        assert stats["total_items"] == 2
        assert stats["latest_items"] == 2


# ── EntityExtractor Tests ─────────────────────────────────────────────────

class TestEntityExtractor:
    """Tests for EntityExtractor."""

    def test_extract_technologies(self):
        """Test technology extraction."""
        extractor = EntityExtractor()
        entities = extractor.extract("Usamos ChromaDB y LadybugDB para EDMS")

        techs = [e for e in entities if e["type"] == "technology"]
        assert len(techs) >= 2

        names = [e["text"] for e in techs]
        assert "ChromaDB" in names
        assert "LadybugDB" in names

    def test_extract_disciplines(self):
        """Test discipline extraction."""
        extractor = EntityExtractor()
        entities = extractor.extract("Aplicamos TDD y BDD en el proyecto")

        disciplines = [e for e in entities if e["type"] == "discipline"]
        assert len(disciplines) >= 2

        names = [e["text"] for e in disciplines]
        assert "TDD" in names
        assert "BDD" in names

    def test_extract_agents(self):
        """Test agent extraction."""
        extractor = EntityExtractor()
        entities = extractor.extract("evol-builder y evol-qa trabajan juntos")

        agents = [e for e in entities if e["type"] == "agent"]
        assert len(agents) >= 2

    def test_extract_relationships(self):
        """Test relationship extraction."""
        extractor = EntityExtractor()
        rels = extractor.extract_relationships("Usamos ChromaDB para vector search")

        assert len(rels) > 0
        assert any(r["type"] == "MENCIONA" for r in rels)

    def test_extract_all(self):
        """Test extract_all returns both entities and relationships."""
        extractor = EntityExtractor()
        result = extractor.extract_all("Usamos ChromaDB para vector search")

        assert "entities" in result
        assert "relationships" in result

    def test_empty_text(self):
        """Test empty text returns empty list."""
        extractor = EntityExtractor()
        assert extractor.extract("") == []
        assert extractor.extract_relationships("") == []


# ── AutoLinker Tests ──────────────────────────────────────────────────────

class TestAutoLinker:
    """Tests for AutoLinker."""

    def test_link_pattern_para(self):
        """Test PARA relationship pattern."""
        linker = AutoLinker()
        links = linker.link("ChromaDB para vector search")

        para_links = [l for l in links if l["relation"] == "PARA"]
        assert len(para_links) > 0

    def test_link_pattern_con(self):
        """Test CON relationship pattern."""
        linker = AutoLinker()
        links = linker.link("Python con FastAPI")

        con_links = [l for l in links if l["relation"] == "CON"]
        assert len(con_links) > 0

    def test_link_pattern_usando(self):
        """Test USANDO relationship pattern."""
        linker = AutoLinker()
        links = linker.link("Sistema usando Docker")

        usando_links = [l for l in links if l["relation"] == "USANDO"]
        assert len(usando_links) > 0

    def test_proximity_links(self):
        """Test proximity-based linking."""
        linker = AutoLinker()
        links = linker.link("ChromaDB y LadybugDB son importantes para EDMS")

        # Should find proximity link between ChromaDB and LadybugDB
        assert len(links) > 0

    def test_empty_text(self):
        """Test empty text returns empty list."""
        linker = AutoLinker()
        assert linker.link("") == []


# ── EntityStore Tests ─────────────────────────────────────────────────────

class TestEntityStore:
    """Tests for EntityStore."""

    def test_upsert_new(self, temp_dir):
        """Test upsert creates new entity."""
        store = EntityStore(temp_dir)
        entity_id = store.upsert("ChromaDB", "technology", {"desc": "Vector DB"})

        assert entity_id is not None
        entity = store.get("ChromaDB")
        assert entity is not None
        assert entity["name"] == "ChromaDB"
        assert entity["type"] == "technology"
        assert entity["version"] == 1
        assert entity["is_latest"] is True

    def test_upsert_update(self, temp_dir):
        """Test upsert updates entity (creates new version)."""
        store = EntityStore(temp_dir)
        store.upsert("ChromaDB", "technology", {"desc": "v1"})
        store.upsert("ChromaDB", "technology", {"desc": "v2"})

        entity = store.get("ChromaDB")
        assert entity["version"] == 2
        assert entity["properties"]["desc"] == "v2"

    def test_get_by_type(self, temp_dir):
        """Test get with type filter."""
        store = EntityStore(temp_dir)
        store.upsert("ChromaDB", "technology")
        store.upsert("Evol-DD", "project")

        tech = store.get("ChromaDB", "technology")
        assert tech is not None

        proj = store.get("ChromaDB", "project")
        assert proj is None

    def test_invalidate(self, temp_dir):
        """Test entity invalidation."""
        store = EntityStore(temp_dir)
        store.upsert("Neo4j", "technology")

        assert store.invalidate("Neo4j", "technology") is True
        entity = store.get("Neo4j")
        assert entity is None  # No longer latest

    def test_add_relation(self, temp_dir):
        """Test adding relations."""
        store = EntityStore(temp_dir)
        store.upsert("ChromaDB", "technology")
        store.upsert("EDMS", "project")

        idx = store.add_relation(
            "ChromaDB", "technology",
            "EDMS", "project",
            "PARA"
        )
        assert idx == 0

        rels = store.get_relations("ChromaDB")
        assert len(rels) == 1
        assert rels[0]["relation"] == "PARA"

    def test_search(self, temp_dir):
        """Test entity search."""
        store = EntityStore(temp_dir)
        store.upsert("ChromaDB", "technology")
        store.upsert("LadybugDB", "technology")

        results = store.search("Chroma")
        assert len(results) > 0
        assert results[0]["name"] == "ChromaDB"

    def test_stats(self, temp_dir):
        """Test stats function."""
        store = EntityStore(temp_dir)
        store.upsert("ChromaDB", "technology")
        store.upsert("Evol-DD", "project")

        stats = store.stats()
        assert stats["latest_entities"] == 2
        assert "technology" in stats["entity_types"]


# ── Integration Tests ─────────────────────────────────────────────────────

class TestMemoryV2Integration:
    """Integration tests for all v2 components together."""

    def test_full_workflow(self, temp_dir):
        """Test complete workflow: store → extract → link → query."""
        # Store verbatim
        verbatim = VerbatimStore(temp_dir)
        text = "Decidimos usar ChromaDB para vector search y LadybugDB para graph database"
        item_id = verbatim.write(text, {"tipo": "decision", "sprint": "F1"})

        # Extract entities
        extractor = EntityExtractor()
        entities = extractor.extract(text)
        assert len(entities) > 0

        # Auto-link
        linker = AutoLinker(extractor)
        links = linker.link(text)
        assert len(links) > 0

        # Store entities
        entity_store = EntityStore(temp_dir)
        for entity in entities:
            entity_store.upsert(
                entity["text"],
                entity["type"],
                {"source": "integration_test"},
                entity.get("confidence", 0.5),
            )

        # Verify
        item = verbatim.read(item_id)
        assert item["verbatim"] == text

        chroma = entity_store.get("ChromaDB", "technology")
        assert chroma is not None

        ladybug = entity_store.get("LadybugDB", "technology")
        assert ladybug is not None

    def test_integrity_verification(self, temp_dir):
        """Test integrity verification across workflow."""
        store = VerbatimStore(temp_dir)
        text = "Integrity test content"
        item_id = store.write(text)

        result = store.verify_integrity(item_id)
        assert result["valid"] is True

    def test_entity_versioning(self, temp_dir):
        """Test entity versioning over time."""
        store = EntityStore(temp_dir)

        # Version 1
        store.upsert("MemorySystem", "concept", {"version": "v1"})
        v1 = store.get("MemorySystem")
        assert v1["version"] == 1

        # Version 2
        store.upsert("MemorySystem", "concept", {"version": "v2"})
        v2 = store.get("MemorySystem")
        assert v2["version"] == 2

        # Old version exists but is not latest
        all_versions = store.get_all(only_latest=False)
        concept_versions = [
            e for e in all_versions
            if e["name"] == "MemorySystem"
        ]
        assert len(concept_versions) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
