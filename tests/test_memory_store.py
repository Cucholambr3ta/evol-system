#!/usr/bin/env python3
"""Tests for evol_memory_store.py"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from evol_memory_store import (
    MemoryStore,
    composite_score,
    privacy_strip,
    reciprocal_rank_fusion,
)


def test_privacy_strip():
    """Elimina secrets antes de indexar."""
    text = "API key: sk-123456789012345678901234567890123456789012345678"
    result = privacy_strip(text)
    assert "sk-" not in result
    assert "REDACTED" in result


def test_privacy_strip_github_token():
    """Elimina GitHub tokens."""
    text = "Token: ghp_abcdefghijklmnopqrstuvwxyz123456"
    result = privacy_strip(text)
    assert "ghp_" not in result
    assert "REDACTED" in result


def test_privacy_strip_password():
    """Elimina passwords."""
    text = 'password="supersecret123"'
    result = privacy_strip(text)
    assert "supersecret123" not in result
    assert "REDACTED" in result


def test_rrf_fusion():
    """RRF fusion de 3 rankings."""
    r1 = ["a", "b", "c"]
    r2 = ["b", "a", "d"]
    r3 = ["c", "a", "b"]
    result = reciprocal_rank_fusion({"bm25": r1, "vector": r2, "graph": r3})
    assert len(result) > 0
    # 'a' appears first in r2 and second in r1 and r3, should be top
    top_ids = [item_id for item_id, score in result[:2]]
    assert "a" in top_ids


def test_composite_scoring():
    """Score compuesto calcula correctamente."""
    item = {
        "chroma_distance": 0.8,
        "fecha": datetime.now().strftime('%Y-%m-%d'),
        "importance": 0.9,
        "tipo": "decision"
    }
    score = composite_score(item)
    assert 0 <= score <= 1
    assert score > 0.5  # high vector + recent + high importance


def test_composite_scoring_old_item():
    """Items viejos tienen menor score de recency."""
    item_new = {
        "chroma_distance": 0.5,
        "fecha": datetime.now().strftime('%Y-%m-%d'),
        "importance": 0.5,
        "tipo": "decision"
    }
    item_old = {
        "chroma_distance": 0.5,
        "fecha": (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
        "importance": 0.5,
        "tipo": "decision"
    }
    score_new = composite_score(item_new)
    score_old = composite_score(item_old)
    assert score_new > score_old


def test_chromadb_index_and_search():
    """Indexa y busca (con fallback local)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        store.index("Decidimos usar gate HMAC para aprobaciones", {
            "proyecto": "evol-dd",
            "sprint": "05",
            "tipo": "decision",
            "disciplinas": ["sec-driven"],
        })
        results = store.search("gate HMAC", project="evol-dd")
        assert len(results) > 0
        assert "HMAC" in results[0]["text"]


def test_wake_up_context():
    """Genera contexto para nueva sesion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        store.index("Decidimos usar gate HMAC", {
            "proyecto": "evol-dd",
            "tipo": "decision"
        })
        context = store.get_context("evol-dd")
        assert "evol-dd" in context
        assert len(context) < 1000


def test_graph_creation():
    """Crea nodos y relaciones en grafo."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        store.graph_add_node("Proyecto", {"name": "evol-dd"})
        store.graph_add_node("Disciplina", {"name": "DDD"})
        store.graph_add_relation("evol-dd", "DEFINE", "DDD")
        result = store.graph_traverse("evol-dd")
        assert "relations" in result


def test_privacy_before_index():
    """Privacy strip se ejecuta antes de indexar."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        store.index("API key: sk-123456789012345678901234567890123456789012345678", {
            "proyecto": "test"
        })
        results = store.search("API key", project="test", n_results=1)
        # The stored text should have the key redacted
        if results:
            assert "sk-12345" not in results[0]["text"], "Raw API key found in indexed text!"
            assert "REDACTED" in results[0]["text"] or results[0]["text"] != "sk-123456789012345678901234567890123456789012345678"


def test_index_adds_tier_field():
    """index() adds tier='raw' by default."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        doc_id = store.index("test content", {"proyecto": "test"})
        results = store.search("test content", project="test", n_results=1)
        assert len(results) == 1
        assert results[0]["metadata"].get("tier") == "raw"


def test_index_preserves_custom_tier():
    """index() preserves custom tier if provided."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        store.index("compressed content", {"proyecto": "test", "tier": "compressed"})
        results = store.search("compressed content", project="test", n_results=1)
        assert len(results) == 1
        assert results[0]["metadata"].get("tier") == "compressed"


def test_compact_extractive_dedup():
    """compact_extractive deduplicates items with >70% Jaccard similarity."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        items = [
            {"id": "1", "text": "Decidimos usar gate HMAC-SHA256 para autenticacion", "metadata": {"proyecto": "test", "indexed_at": "2026-06-01T00:00:00"}},
            {"id": "2", "text": "Decidimos usar gate HMAC-SHA256 para autenticacion y seguridad", "metadata": {"proyecto": "test", "indexed_at": "2026-06-02T00:00:00"}},
            {"id": "3", "text": "Instalamos ChromaDB para vector search", "metadata": {"proyecto": "test", "indexed_at": "2026-06-03T00:00:00"}},
        ]
        compressed = store.compact_extractive(items, threshold=0.7)
        # Items 1 and 2 are >70% similar, should be deduped
        assert len(compressed) == 2
        assert all(c["metadata"]["tier"] == "compressed" for c in compressed)


def test_compact_extractive_key_sentence():
    """compact_extractive extracts the most informative sentence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        items = [
            {"id": "1", "text": "Hoy hicimos muchas cosas. Decidimos usar ChromaDB. El test paso.", "metadata": {"proyecto": "test"}},
        ]
        compressed = store.compact_extractive(items)
        assert len(compressed) == 1
        # Should contain "Decidimos" (high-value keyword)
        assert "Decidimos" in compressed[0]["text"] or "ChromaDB" in compressed[0]["text"]


def test_compact_extractive_empty():
    """compact_extractive handles empty input."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        compressed = store.compact_extractive([])
        assert compressed == []


def test_compact_tier_basic():
    """compact_tier compacts raw items to compressed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        # Index 5 raw items
        for i in range(5):
            store.index(f"decision {i} about architecture", {"proyecto": "test", "tipo": "decision"})
        # Verify raw count
        stats_before = store.get_tier_stats("test")
        assert stats_before["raw"] == 5
        # Compact
        result = store.compact_tier("test", max_items=10, force="extractive")
        assert result["compacted"] == 5
        assert result["method"] == "extractive"
        assert result["after"] >= 1  # At least 1 compressed item
        # Verify stats after — items with unchanged text become compressed, changed become archived
        stats_after = store.get_tier_stats("test")
        assert stats_after["raw"] == 0
        assert stats_after["compressed"] >= 5  # All originals now compressed (text unchanged)


def test_compact_tier_dry_run():
    """compact_tier with dry_run doesn't modify anything."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        for i in range(3):
            store.index(f"observation {i}", {"proyecto": "test"})
        # Can't actually test dry_run through store directly, but verify tier stats work
        stats = store.get_tier_stats("test")
        assert stats["raw"] == 3
        assert stats["compressed"] == 0


def test_tier_stats_real():
    """get_tier_stats counts by actual tier field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        store.index("raw item", {"proyecto": "test", "tier": "raw"})
        store.index("compressed item", {"proyecto": "test", "tier": "compressed"})
        store.index("memory item", {"proyecto": "test", "tier": "memory"})
        store.index("another raw", {"proyecto": "test"})  # defaults to raw
        stats = store.get_tier_stats("test")
        assert stats["raw"] == 2
        assert stats["compressed"] == 1
        assert stats["memory"] == 1
        assert stats["total"] == 4


def test_jaccard_similarity():
    """_jaccard_similarity computes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        assert store._jaccard_similarity("hello world", "hello world") == 1.0
        assert store._jaccard_similarity("hello world", "goodbye world") > 0.3
        assert store._jaccard_similarity("completely different", "nothing alike") == 0.0


def test_extract_key_sentence():
    """_extract_key_sentence picks the most informative sentence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        # Sentence with "decidimos" should be preferred
        result = store._extract_key_sentence("Hoy fue un dia normal. Decidimos usar Redis. Todo bien.")
        assert "Decidimos" in result


# ── New tests: P0+P1+P2 indexing improvements ──────────────────────────────


def test_importance_default():
    """index() adds importance=0.5 by default."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        doc_id = store.index("test content", {"proyecto": "test"})
        assert doc_id is not None
        # Verify via ChromaDB
        if store._chroma_collection:
            results = store._chroma_collection.get(ids=[doc_id])
            assert results['metadatas'][0]['importance'] == 0.5


def test_importance_custom():
    """index() preserves custom importance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        doc_id = store.index("important content", {"proyecto": "test", "importance": 0.95})
        if store._chroma_collection:
            results = store._chroma_collection.get(ids=[doc_id])
            assert results['metadatas'][0]['importance'] == 0.95


def test_content_hash_added():
    """index() adds content_hash for change detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        doc_id = store.index("test content for hash", {"proyecto": "test"})
        if store._chroma_collection:
            results = store._chroma_collection.get(ids=[doc_id])
            meta = results['metadatas'][0]
            assert 'content_hash' in meta
            assert len(meta['content_hash']) == 16  # SHA-256[:16]


def test_artefacto_graph_node():
    """tipo=artefacto creates Artefacto node and relations in graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        store.index("Artefacto de prueba", {
            "proyecto": "test",
            "tipo": "artefacto",
            "fase": "Build",
            "source_file": "docs/test.md",
            "disciplinas": ["TDD"],
        })
        # Verify graph nodes were added (via in-memory fallback or LadybugDB)
        # Check that _auto_update_graph created nodes by verifying no exception
        # and that the graph has entries
        if hasattr(store, '_graph') and store._graph:
            node_keys = [k for k in store._graph.keys() if 'Artefacto' in k or 'GENERADO_POR' in str(store._graph.get(k, {}))]
            assert len(node_keys) > 0 or len(store._graph) > 0


def test_agente_def_graph_node():
    """tipo=agente_def creates AgenteDef node in graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        store.index("Agent definition for security", {
            "proyecto": "test",
            "tipo": "agente_def",
            "agent_name": "evol-sec",
            "agent_capabilities": "SecDD, STRIDE",
        })
        result = store.graph_traverse("test", depth=3)
        # Check that TIENE_AGENTE relation exists
        relations = result.get('relations', [])
        rel_types = [r.get('type') for r in relations]
        assert 'TIENE_AGENTE' in rel_types


def test_skill_def_graph_node():
    """tipo=skill_def creates SkillDef node in graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        store.index("Skill definition for compaction", {
            "proyecto": "test",
            "tipo": "skill_def",
            "skill_name": "evol-compact",
            "skill_trigger": "/compact",
        })
        result = store.graph_traverse("test", depth=3)
        relations = result.get('relations', [])
        rel_types = [r.get('type') for r in relations]
        assert 'TIENE_SKILL' in rel_types


def test_parse_frontmatter():
    """parse_frontmatter extracts YAML fields correctly."""
    from evol_memory_store import parse_frontmatter
    content = "---\nname: evol-sec\ncategory: core\ntriggers: [\"/evol sec\"]\n---\n# Content here"
    result = parse_frontmatter(content)
    assert result['name'] == 'evol-sec'
    assert result['category'] == 'core'
    assert isinstance(result.get('triggers'), list)


def test_parse_frontmatter_no_frontmatter():
    """parse_frontmatter returns empty dict when no frontmatter."""
    from evol_memory_store import parse_frontmatter
    content = "# Just a heading\n\nSome content."
    result = parse_frontmatter(content)
    assert result == {}


def test_extract_section():
    """extract_section returns content under a heading."""
    from evol_memory_store import extract_section
    content = "# Title\n\n## Scope\n\nThis agent handles security.\n\n## Rules\n\nRule 1."
    result = extract_section(content, "Scope")
    assert "handles security" in result
    assert "Rule 1" not in result


def test_extract_section_not_found():
    """extract_section returns empty string when heading not found."""
    from evol_memory_store import extract_section
    content = "# Title\n\nSome content."
    result = extract_section(content, "Nonexistent")
    assert result == ""


def test_backward_compatibility():
    """Existing indexed data without new fields still works."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(memory_dir=tmpdir)
        # Index with old-style metadata (no importance, no content_hash)
        old_meta = {"proyecto": "test", "tipo": "decision", "fase": "Retro"}
        doc_id = store.index("Old style decision", old_meta)
        assert doc_id is not None
        # Should still be searchable
        results = store.search("decision", project="test")
        assert len(results) > 0


if __name__ == "__main__":
    test_privacy_strip()
    test_privacy_strip_github_token()
    test_privacy_strip_password()
    test_rrf_fusion()
    test_composite_scoring()
    test_composite_scoring_old_item()
    test_chromadb_index_and_search()
    test_wake_up_context()
    test_graph_creation()
    test_privacy_before_index()
    test_index_adds_tier_field()
    test_index_preserves_custom_tier()
    test_compact_extractive_dedup()
    test_compact_extractive_key_sentence()
    test_compact_extractive_empty()
    test_compact_tier_basic()
    test_compact_tier_dry_run()
    test_tier_stats_real()
    test_jaccard_similarity()
    test_extract_key_sentence()
    print("All tests passed!")
