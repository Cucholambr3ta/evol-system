#!/usr/bin/env python3
"""Tests for evol_code_indexer.py — Tree-sitter code graph."""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from evol_code_indexer import (
    parse_file,
    CodeGraph,
    index_project,
)


def test_parse_python_function():
    """Parse Python function with Tree-sitter."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write('''def hello_world():
    """Greet the world."""
    print("Hello, world!")

def add(a, b):
    return a + b
''')
        f.flush()
        result = parse_file(Path(f.name))

    os.unlink(f.name)

    assert "error" not in result
    assert result["language"] == "python"
    assert len(result["symbols"]) == 2
    assert result["symbols"][0]["name"] == "hello_world"
    assert result["symbols"][0]["kind"] == "Function"
    assert result["symbols"][0]["docstring"] == "Greet the world."
    assert result["symbols"][1]["name"] == "add"


def test_parse_python_class():
    """Parse Python class with methods."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write('''class MyClass:
    """A test class."""
    
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1
        return self.value
''')
        f.flush()
        result = parse_file(Path(f.name))

    os.unlink(f.name)

    assert "error" not in result
    assert len(result["symbols"]) >= 3  # MyClass, __init__, increment
    class_syms = [s for s in result["symbols"] if s["kind"] == "Class"]
    assert len(class_syms) == 1
    assert class_syms[0]["name"] == "MyClass"

    method_syms = [s for s in result["symbols"] if s["kind"] == "Method"]
    assert len(method_syms) >= 2


def test_parse_python_imports():
    """Parse Python imports."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write('''import os
import sys
from pathlib import Path
from evol_memory_store import MemoryStore
''')
        f.flush()
        result = parse_file(Path(f.name))

    os.unlink(f.name)

    assert "error" not in result
    assert len(result["imports"]) == 4
    modules = [i["module"] for i in result["imports"]]
    assert "os" in modules
    assert "pathlib" in modules
    assert "evol_memory_store" in modules


def test_parse_python_calls():
    """Parse Python function calls."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write('''def caller():
    callee_one()
    callee_two()
    
def callee_one():
    pass

def callee_two():
    pass
''')
        f.flush()
        result = parse_file(Path(f.name))

    os.unlink(f.name)

    assert "error" not in result
    calls = [c for c in result["calls"] if c.get("_relation") == "CALLS"]
    assert len(calls) == 2
    callees = [c["_callee"] for c in calls]
    assert "callee_one" in callees
    assert "callee_two" in callees


def test_parse_javascript_function():
    """Parse JavaScript function."""
    with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
        f.write('''function greet(name) {
    return "Hello, " + name;
}

const add = (a, b) => a + b;
''')
        f.flush()
        result = parse_file(Path(f.name))

    os.unlink(f.name)

    assert "error" not in result
    assert result["language"] == "javascript"
    assert len(result["symbols"]) >= 1
    names = [s["name"] for s in result["symbols"]]
    assert "greet" in names


def test_code_graph_add_node():
    """CodeGraph adds nodes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        node_id = graph.add_node("Symbol", {
            "name": "test_func",
            "kind": "Function",
            "line": 10,
        })

        assert node_id == "test_func"


def test_code_graph_add_relation():
    """CodeGraph adds relations correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        graph.add_node("Symbol", {"name": "caller"})
        graph.add_node("Symbol", {"name": "callee"})

        result = graph.add_relation("caller", "CALLS", "callee")
        assert result is True


def test_code_graph_traverse():
    """CodeGraph traverses from a node."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        graph.add_node("Symbol", {"name": "A"})
        graph.add_node("Symbol", {"name": "B"})
        graph.add_node("Symbol", {"name": "C"})
        graph.add_relation("A", "CALLS", "B")
        graph.add_relation("B", "CALLS", "C")

        result = graph.traverse("A", depth=2)
        node_names = [n["name"] for n in result["nodes"]]
        assert "B" in node_names or "C" in node_names


def test_code_graph_impact():
    """CodeGraph calculates impact (blast radius)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        graph.add_node("Symbol", {"name": "target"})
        graph.add_node("Symbol", {"name": "caller1"})
        graph.add_node("Symbol", {"name": "caller2"})
        graph.add_relation("caller1", "CALLS", "target")
        graph.add_relation("caller2", "CALLS", "target")

        impact = graph.get_impact("target", max_depth=1)
        assert impact["total_affected"] == 2
        assert len(impact["depths"]) == 1
        assert impact["depths"][0]["count"] == 2


def test_code_graph_stats():
    """CodeGraph returns statistics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = CodeGraph(memory_dir=tmpdir)

        graph.add_node("Symbol", {"name": "A"})
        graph.add_node("File", {"name": "test.py"})
        graph.add_relation("A", "CALLS", "B")

        stats = graph.stats()
        assert stats["total_nodes"] >= 2
        assert stats["total_relations"] >= 1


def test_index_project():
    """Index a project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create a Python file
        py_file = project_root / "test_module.py"
        py_file.write_text('''def hello():
    print("hello")

def world():
    hello()
    print("world")
''')

        graph = CodeGraph(memory_dir=tmpdir)
        stats = index_project(project_root, incremental=False, graph=graph)

        assert stats["files_indexed"] >= 1
        assert stats["symbols_found"] >= 2


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
