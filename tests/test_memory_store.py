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
        results = store.search("sk-", project="test")
        assert len(results) == 0  # should not find the raw key


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
    print("All tests passed!")
