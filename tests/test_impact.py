#!/usr/bin/env python3
"""Tests for impact analysis and process tracing."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from evol_code_indexer import CodeGraph


def test_impact_direct_callers():
    """Impact analysis finds direct callers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        # Build a simple call graph: A -> B -> C
        graph.add_node("Symbol", {"name": "target"})
        graph.add_node("Symbol", {"name": "caller1"})
        graph.add_node("Symbol", {"name": "caller2"})
        graph.add_relation("caller1", "CALLS", "target")
        graph.add_relation("caller2", "CALLS", "target")

        impact = graph.get_impact("target", max_depth=1)
        assert impact["total_affected"] == 2
        assert len(impact["depths"]) == 1
        assert impact["depths"][0]["count"] == 2
        assert "caller1" in impact["depths"][0]["callers"]
        assert "caller2" in impact["depths"][0]["callers"]


def test_impact_indirect_callers():
    """Impact analysis finds indirect callers (depth 2)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        # Build: A -> B -> C -> target
        graph.add_node("Symbol", {"name": "target"})
        graph.add_node("Symbol", {"name": "B"})
        graph.add_node("Symbol", {"name": "A"})
        graph.add_relation("B", "CALLS", "target")
        graph.add_relation("A", "CALLS", "B")

        impact = graph.get_impact("target", max_depth=2)
        assert impact["total_affected"] == 2
        assert len(impact["depths"]) == 2
        # Depth 1: B calls target
        assert impact["depths"][0]["count"] == 1
        assert "B" in impact["depths"][0]["callers"]
        # Depth 2: A calls B (indirectly affects target)
        assert impact["depths"][1]["count"] == 1
        assert "A" in impact["depths"][1]["callers"]


def test_impact_no_callers():
    """Impact analysis returns empty when no callers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        graph.add_node("Symbol", {"name": "isolated"})

        impact = graph.get_impact("isolated", max_depth=3)
        assert impact["total_affected"] == 0
        assert len(impact["depths"]) == 0


def test_trace_entry_point():
    """Process tracing follows call chain from entry point."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        # Build: entry -> A -> B -> C
        graph.add_node("Symbol", {"name": "entry"})
        graph.add_node("Symbol", {"name": "A"})
        graph.add_node("Symbol", {"name": "B"})
        graph.add_node("Symbol", {"name": "C"})
        graph.add_relation("entry", "CALLS", "A")
        graph.add_relation("A", "CALLS", "B")
        graph.add_relation("B", "CALLS", "C")

        trace = graph.get_trace("entry", max_depth=5)
        assert trace["entry"] == "entry"
        assert len(trace["steps"]) == 4
        step_symbols = [s["symbol"] for s in trace["steps"]]
        assert "entry" in step_symbols
        assert "A" in step_symbols
        assert "B" in step_symbols
        assert "C" in step_symbols


def test_trace_with_cycle():
    """Process tracing handles circular dependencies."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        # Build cycle: A -> B -> A
        graph.add_node("Symbol", {"name": "A"})
        graph.add_node("Symbol", {"name": "B"})
        graph.add_relation("A", "CALLS", "B")
        graph.add_relation("B", "CALLS", "A")

        trace = graph.get_trace("A", max_depth=5)
        # Should not infinite loop
        assert len(trace["steps"]) <= 50
        step_symbols = [s["symbol"] for s in trace["steps"]]
        assert "A" in step_symbols
        assert "B" in step_symbols


def test_trace_max_depth():
    """Process tracing respects max depth."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        # Build: A -> B -> C -> D -> E
        graph.add_node("Symbol", {"name": "A"})
        graph.add_node("Symbol", {"name": "B"})
        graph.add_node("Symbol", {"name": "C"})
        graph.add_node("Symbol", {"name": "D"})
        graph.add_node("Symbol", {"name": "E"})
        graph.add_relation("A", "CALLS", "B")
        graph.add_relation("B", "CALLS", "C")
        graph.add_relation("C", "CALLS", "D")
        graph.add_relation("D", "CALLS", "E")

        trace = graph.get_trace("A", max_depth=2)
        # Should only go 2 levels deep
        assert len(trace["steps"]) <= 3  # A + B + C


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
