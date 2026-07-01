"""Tests for EDMS Memory v2.0 Phase 2 - Hybrid Retrieval Components."""

import os
import tempfile
import pytest
from pathlib import Path

# Add scripts dir to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evol_memory_v2.bm25_retriever import BM25Retriever, tokenize, BM25Params
from evol_memory_v2.evidence import (
    EvidenceContract, EvidenceSource, EvidenceTemporal,
    EvidenceBuilder, create_evidence_from_result,
)
from evol_memory_v2.graph_expander import GraphExpander, GraphNode, GraphEdge
from evol_memory_v2.hybrid_retriever import HybridRetriever, RetrievalResult


# ============================================================================
# BM25 Retriever Tests
# ============================================================================

class TestTokenize:
    """Tests for tokenizer."""

    def test_basic_tokenization(self):
        tokens = tokenize("ChromaDB es una librería de vectores")
        assert "chromadb" in tokens
        assert "vectores" in tokens
        # Stop words removed
        assert "es" not in tokens
        assert "una" not in tokens
        assert "de" not in tokens

    def test_lowercasing(self):
        tokens = tokenize("CHROMADB Vector SEARCH")
        assert all(t.islower() for t in tokens)

    def test_short_tokens_removed(self):
        tokens = tokenize("a bb ccc dddd")
        assert "a" not in tokens
        assert "bb" not in tokens
        assert "ccc" in tokens
        assert "dddd" in tokens

    def test_punctuation_removed(self):
        tokens = tokenize("hello, world! how's it?")
        assert "," not in " ".join(tokens)
        assert "!" not in " ".join(tokens)


class TestBM25Retriever:
    """Tests for BM25 retriever."""

    def test_add_and_search(self):
        retriever = BM25Retriever()
        retriever.add("doc1", "ChromaDB es una librería de vectores")
        retriever.add("doc2", "LadybugDB es una base de grafos")
        retriever.add("doc3", "ChromaDB y LadybugDB son complementarias")

        results = retriever.search("ChromaDB vectores")
        assert len(results) > 0
        assert results[0]["id"] == "doc1"

    def test_update_document(self):
        retriever = BM25Retriever()
        retriever.add("doc1", "ChromaDB es una librería")
        retriever.add("doc1", "ChromaDB es una base de datos")

        results = retriever.search("base de datos")
        assert len(results) > 0
        assert results[0]["id"] == "doc1"

    def test_remove_document(self):
        retriever = BM25Retriever()
        retriever.add("doc1", "ChromaDB es una librería")
        retriever.add("doc2", "LadybugDB es una base de grafos")

        retriever.remove_document("doc1")
        results = retriever.search("ChromaDB")
        assert len(results) == 0

    def test_empty_query(self):
        retriever = BM25Retriever()
        retriever.add("doc1", "ChromaDB es una librería")

        results = retriever.search("")
        assert len(results) == 0

    def test_no_results(self):
        retriever = BM25Retriever()
        retriever.add("doc1", "ChromaDB es una librería")

        results = retriever.search("xyz", min_score=10.0)
        assert len(results) == 0

    def test_metadata_preserved(self):
        retriever = BM25Retriever()
        retriever.add("doc1", "ChromaDB", {"tier": "memory", "tipo": "tecnologia"})

        results = retriever.search("ChromaDB")
        assert results[0]["metadata"]["tier"] == "memory"
        assert results[0]["metadata"]["tipo"] == "tecnologia"

    def test_stats(self):
        retriever = BM25Retriever()
        retriever.add("doc1", "ChromaDB es una librería")
        retriever.add("doc2", "LadybugDB es una base de grafos")

        stats = retriever.stats()
        assert stats["total_documents"] == 2
        assert stats["total_terms"] > 0

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bm25_index.json"

            retriever = BM25Retriever()
            retriever.add("doc1", "ChromaDB es una librería")
            retriever.add("doc2", "LadybugDB es una base de grafos")
            retriever.save(path)

            loaded = BM25Retriever.load(path)
            assert loaded.stats()["total_documents"] == 2

            results = loaded.search("ChromaDB")
            assert len(results) > 0

    def test_top_k_limit(self):
        retriever = BM25Retriever()
        for i in range(20):
            retriever.add(f"doc{i}", f"Documento número {i} sobre ChromaDB")

        results = retriever.search("ChromaDB", top_k=5)
        assert len(results) <= 5

    def test_bm25_params(self):
        params = BM25Params(k1=2.0, b=0.5)
        retriever = BM25Retriever(params)
        retriever.add("doc1", "ChromaDB es una librería")

        results = retriever.search("ChromaDB")
        assert len(results) > 0


# ============================================================================
# Evidence Tests
# ============================================================================

class TestEvidenceSource:
    """Tests for EvidenceSource."""

    def test_creation(self):
        source = EvidenceSource("verbatim", "doc-123", confidence=0.9)
        assert source.type == "verbatim"
        assert source.id == "doc-123"
        assert source.confidence == 0.9
        assert source.timestamp  # Auto-generated

    def test_to_dict(self):
        source = EvidenceSource("summary", "doc-456", confidence=0.8)
        d = source.to_dict()
        assert d["type"] == "summary"
        assert d["id"] == "doc-456"
        assert d["confidence"] == 0.8


class TestEvidenceTemporal:
    """Tests for EvidenceTemporal."""

    def test_creation(self):
        temporal = EvidenceTemporal(valid_from="2026-01-01", valid_to="2026-12-31")
        assert temporal.valid_from == "2026-01-01"
        assert temporal.valid_to == "2026-12-31"
        assert temporal.is_current is True

    def test_is_valid_at(self):
        temporal = EvidenceTemporal(valid_from="2026-01-01", valid_to="2026-12-31")
        assert temporal.is_valid_at("2026-06-15") is True
        assert temporal.is_valid_at("2027-01-01") is False
        assert temporal.is_valid_at("2025-01-01") is False


class TestEvidenceContract:
    """Tests for EvidenceContract."""

    def test_creation(self):
        contract = EvidenceContract(item_id="doc-123")
        assert contract.item_id == "doc-123"
        assert contract.sources == []
        assert contract.confidence == 1.0

    def test_add_source(self):
        contract = EvidenceContract(item_id="doc-123")
        contract.add_source("verbatim", "session-456", confidence=0.9)
        assert len(contract.sources) == 1
        assert contract.sources[0].type == "verbatim"

    def test_add_relationship(self):
        contract = EvidenceContract(item_id="doc-123")
        contract.add_relationship("doc-123", "doc-456", "DERIVED_FROM")
        assert len(contract.relationships) == 1

    def test_to_dict(self):
        contract = EvidenceContract(item_id="doc-123", reasoning="Test reasoning")
        d = contract.to_dict()
        assert d["item_id"] == "doc-123"
        assert d["reasoning"] == "Test reasoning"


class TestEvidenceBuilder:
    """Tests for EvidenceBuilder."""

    def test_build(self):
        contract = (
            EvidenceBuilder()
            .for_item("doc-123")
            .with_source("verbatim", "session-456", confidence=0.9)
            .with_reasoning("Matched on keyword")
            .with_confidence(0.85)
            .build()
        )
        assert contract.item_id == "doc-123"
        assert len(contract.sources) == 1
        assert contract.reasoning == "Matched on keyword"
        assert contract.confidence == 0.85

    def test_chaining(self):
        contract = (
            EvidenceBuilder()
            .for_item("doc-123")
            .with_source("vector", "v1")
            .with_source("bm25", "b1")
            .with_metadata("tier", "memory")
            .build()
        )
        assert len(contract.sources) == 2
        assert contract.metadata["tier"] == "memory"

    def test_missing_item_id(self):
        with pytest.raises(ValueError):
            EvidenceBuilder().build()


class TestCreateEvidenceFromResult:
    """Tests for create_evidence_from_result."""

    def test_create(self):
        result = {"id": "doc-123", "score": 0.85, "text": "Test", "metadata": {"tier": "memory"}}
        contract = create_evidence_from_result(result)
        assert contract.item_id == "doc-123"
        assert contract.confidence == 0.85


# ============================================================================
# Graph Expander Tests
# ============================================================================

class TestGraphExpander:
    """Tests for GraphExpander."""

    def test_add_node(self):
        expander = GraphExpander()
        node_id = expander.add_node("ChromaDB", "technology")
        assert node_id == "chromadb"
        assert expander.get_node("ChromaDB") is not None

    def test_add_edge(self):
        expander = GraphExpander()
        expander.add_node("ChromaDB", "technology")
        expander.add_node("vector search", "concept")
        expander.add_edge("ChromaDB", "vector search", "ENABLES")

        related = expander.get_related("ChromaDB")
        assert len(related) == 1
        assert related[0][0] == "vector search"
        assert related[0][1] == "ENABLES"

    def test_expand(self):
        expander = GraphExpander()
        expander.add_node("ChromaDB", "technology")
        expander.add_node("vector search", "concept")
        expander.add_edge("ChromaDB", "vector search", "ENABLES")

        expanded = expander.expand("ChromaDB")
        assert "chromadb" in expanded
        assert "vector search" in expanded

    def test_expand_no_match(self):
        expander = GraphExpander()
        expanded = expander.expand("xyz")
        assert "xyz" in expanded

    def test_stats(self):
        expander = GraphExpander()
        expander.add_node("ChromaDB", "technology")
        expander.add_node("LadybugDB", "technology")
        expander.add_edge("ChromaDB", "LadybugDB", "RELATED_TO")

        stats = expander.stats()
        assert stats["nodes"] == 2
        assert stats["edges"] == 1

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"

            expander = GraphExpander()
            expander.add_node("ChromaDB", "technology")
            expander.add_node("vector search", "concept")
            expander.add_edge("ChromaDB", "vector search", "ENABLES")
            expander.save(path)

            loaded = GraphExpander.load(path)
            assert loaded.stats()["nodes"] == 2


# ============================================================================
# Hybrid Retriever Tests
# ============================================================================

class TestHybridRetriever:
    """Tests for HybridRetriever."""

    def test_add_and_search(self):
        retriever = HybridRetriever(use_vector=False)
        retriever.add_document("doc1", "ChromaDB es una librería de vectores")
        retriever.add_document("doc2", "LadybugDB es una base de grafos")
        retriever.add_document("doc3", "ChromaDB y LadybugDB son complementarias")

        results = retriever.search("ChromaDB", top_k=3)
        assert len(results) > 0
        assert any("ChromaDB" in r.text for r in results)

    def test_retrieval_sources(self):
        retriever = HybridRetriever(use_vector=False)
        retriever.add_document("doc1", "ChromaDB es una librería")

        results = retriever.search("ChromaDB")
        assert len(results) > 0
        assert "bm25" in results[0].retrieval_sources

    def test_evidence_contracts(self):
        retriever = HybridRetriever(use_vector=False)
        retriever.add_document("doc1", "ChromaDB es una librería")

        results = retriever.search("ChromaDB", include_evidence=True)
        assert len(results) > 0
        assert results[0].evidence is not None
        assert results[0].evidence.item_id == "doc1"

    def test_no_evidence(self):
        retriever = HybridRetriever(use_vector=False)
        retriever.add_document("doc1", "ChromaDB es una librería")

        results = retriever.search("ChromaDB", include_evidence=False)
        assert len(results) > 0
        assert results[0].evidence is None

    def test_empty_query(self):
        retriever = HybridRetriever(use_vector=False)
        retriever.add_document("doc1", "ChromaDB es una librería")

        results = retriever.search("")
        assert len(results) == 0

    def test_top_k_limit(self):
        retriever = HybridRetriever(use_vector=False)
        for i in range(20):
            retriever.add_document(f"doc{i}", f"Documento {i} sobre ChromaDB")

        results = retriever.search("ChromaDB", top_k=5)
        assert len(results) <= 5

    def test_stats(self):
        retriever = HybridRetriever(use_vector=False)
        retriever.add_document("doc1", "ChromaDB es una librería")

        stats = retriever.stats()
        assert stats["documents"] == 1
        assert stats["bm25"] is not None
        assert stats["graph"] is not None
        assert stats["vector_store"] == "disconnected"


# ============================================================================
# Integration Tests
# ============================================================================

class TestPhase2Integration:
    """Integration tests for Phase 2 components."""

    def test_full_workflow(self):
        """Test complete Phase 2 workflow."""
        # Create hybrid retriever
        retriever = HybridRetriever(use_vector=False)

        # Add documents
        retriever.add_document(
            "doc1",
            "Decidimos usar ChromaDB para vector search en EDMS",
            {"tier": "memory", "tipo": "decision"},
        )
        retriever.add_document(
            "doc2",
            "LadybugDB es la base de grafos principal",
            {"tier": "memory", "tipo": "leccion"},
        )
        retriever.add_document(
            "doc3",
            "ChromaDB y LadybugDB son complementarias para EDMS",
            {"tier": "knowledge", "tipo": "decision"},
        )

        # Search
        results = retriever.search("ChromaDB grafos")

        # Verify results
        assert len(results) > 0
        assert results[0].score > 0
        assert results[0].evidence is not None
        assert results[0].evidence.confidence > 0

    def test_evidence_with_relationships(self):
        """Test evidence contracts with relationships."""
        contract = (
            EvidenceBuilder()
            .for_item("doc-123")
            .with_source("verbatim", "session-456")
            .with_source("vector", "embedding-789")
            .with_relationship("doc-123", "doc-456", "DERIVED_FROM")
            .with_temporal(valid_from="2026-01-01", valid_to="2026-12-31")
            .with_reasoning("Hybrid retrieval matched on multiple signals")
            .with_confidence(0.92)
            .build()
        )

        d = contract.to_dict()
        assert len(d["sources"]) == 2
        assert len(d["relationships"]) == 1
        assert d["temporal"]["valid_from"] == "2026-01-01"

    def test_graph_expansion(self):
        """Test graph expansion improves recall."""
        retriever = HybridRetriever(use_vector=False, use_graph=True)

        # Add documents with related terms
        retriever.add_document(
            "doc1",
            "ChromaDB es una librería de vectores",
            {"tipo": "tecnologia"},
        )
        retriever.add_document(
            "doc2",
            "El search semántico usa embeddings",
            {"tipo": "concepto"},
        )

        # Search with expansion
        results = retriever.search("ChromaDB")

        # Should find related documents
        assert len(results) > 0
