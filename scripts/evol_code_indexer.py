#!/usr/bin/env python3
"""evol_code_indexer.py — Tree-sitter code graph for Evol-DD.

Parses source code using Tree-sitter AST to extract symbols (functions,
classes, methods), imports, and call relationships. Stores in a separate
LadybugDB graph (evol_dd_codigo.lbug) for impact analysis and process tracing.

Usage:
    python scripts/evol_code_indexer.py index [path]   # Index code
    python scripts/evol_code_indexer.py query <symbol>  # Search symbol
    python scripts/evol_code_indexer.py graph <symbol>  # Dependency graph
    python scripts/evol_code_indexer.py impact <symbol> # Blast radius
    python scripts/evol_code_indexer.py stats           # Statistics
"""

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ── Trace emitter (optional, fails silently) ─────────────────────────────
try:
    from evol_traces import emit_graph_node, emit_graph_relation
    _TRACES_AVAILABLE = True
except ImportError:
    _TRACES_AVAILABLE = False
    def emit_graph_node(*a, **kw): pass
    def emit_graph_relation(*a, **kw): pass

# ── Tree-sitter import (required) ─────────────────────────────────────────
try:
    import tree_sitter
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print("[evol-code-indexer] ERROR: tree-sitter not installed.", file=sys.stderr)
    print("  Install: pip install tree-sitter tree-sitter-python tree-sitter-javascript", file=sys.stderr)
    sys.exit(1)

# ── Language grammars ──────────────────────────────────────────────────────
_GRAMMAR_MODULES = {
    ".py": "tree_sitter_python",
    ".js": "tree_sitter_javascript",
    ".jsx": "tree_sitter_javascript",
    ".ts": "tree_sitter_typescript",
    ".tsx": "tree_sitter_typescript",
}

_EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
}

# ── Auto-detect project venv ──────────────────────────────────────────────
_VENV_PYTHON = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python3"
if _VENV_PYTHON.exists() and sys.executable != str(_VENV_PYTHON):
    try:
        import tree_sitter  # noqa: F401
    except ImportError:
        os.execv(str(_VENV_PYTHON), [str(_VENV_PYTHON)] + sys.argv)

# ── LadybugDB import (optional, fallback to JSON) ─────────────────────────
try:
    import ladybug as lb
    LADYBUG_AVAILABLE = True
except ImportError:
    LADYBUG_AVAILABLE = False

# ── Constants ──────────────────────────────────────────────────────────────
CODE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java"}
SKIP_DIRS = {
    "__pycache__", "node_modules", ".git", ".venv", "venv", "env",
    ".evol", "dist", "build", "*.egg-info", ".mypy_cache", ".pytest_cache",
}
MAX_FILE_SIZE = 500_000  # 500KB max per file
LAST_INDEX_MARKER = ".evol/.last-code-index-commit"


# ── Parser Cache ───────────────────────────────────────────────────────────
_parser_cache: dict[str, Parser] = {}


def _get_parser(language: str) -> Parser:
    """Get or create a Tree-sitter parser for a language."""
    if language in _parser_cache:
        return _parser_cache[language]

    try:
        mod_name = {
            "python": "tree_sitter_python",
            "javascript": "tree_sitter_javascript",
            "typescript": "tree_sitter_typescript",
        }.get(language)

        if not mod_name:
            raise ValueError(f"Unsupported language: {language}")

        import importlib
        mod = importlib.import_module(mod_name)
        lang = Language(mod.language())
        parser = Parser(lang)
        _parser_cache[language] = parser
        return parser
    except Exception as e:
        print(f"[evol-code-indexer] WARN: Could not load grammar for {language}: {e}", file=sys.stderr)
        raise


# ── AST Extraction ─────────────────────────────────────────────────────────

def _extract_imports(node, source_bytes: bytes) -> list[dict]:
    """Extract import statements from AST node."""
    imports = []
    for child in node.children:
        if child.type == "import_statement":
            # import x, import x.y
            text = source_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="replace")
            for mod in re.findall(r'import\s+([\w.]+)', text):
                imports.append({"module": mod, "name": mod.split(".")[-1], "line": child.start_point[0] + 1})
        elif child.type == "import_from_statement":
            # from x import y, z
            text = source_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="replace")
            match = re.match(r'from\s+([\w.]+)\s+import\s+(.+)', text)
            if match:
                module = match.group(1)
                names = [n.strip().split(" as ")[0] for n in match.group(2).split(",")]
                for name in names:
                    imports.append({"module": module, "name": name, "line": child.start_point[0] + 1})
        elif child.type == "import_statement":
            # JS/TS: import x from 'y'
            text = source_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="replace")
            match = re.search(r"from\s+['\"]([^'\"]+)['\"]", text)
            if match:
                imports.append({"module": match.group(1), "name": "*", "line": child.start_point[0] + 1})
    return imports


def _extract_symbols(node, source_bytes: bytes, depth: int = 0) -> list[dict]:
    """Extract function/class/method definitions from AST node."""
    symbols = []
    for child in node.children:
        # Python function_definition
        if child.type == "function_definition":
            name_node = child.child_by_field_name("name")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                body = child.child_by_field_name("body")
                docstring = ""
                if body and body.children:
                    first_stmt = body.children[0] if body.children else None
                    if first_stmt and first_stmt.type == "expression_statement":
                        expr = first_stmt.children[0] if first_stmt.children else None
                        if expr and expr.type == "string":
                            docstring = source_bytes[expr.start_byte:expr.end_byte].decode("utf-8", errors="replace").strip("\"'")

                symbols.append({
                    "name": name,
                    "kind": "Function",
                    "line": child.start_point[0] + 1,
                    "end_line": child.end_point[0] + 1,
                    "docstring": docstring[:200],
                })

                if body:
                    _extract_calls(body, source_bytes, name, symbols)

        # JavaScript/TS function_declaration
        elif child.type == "function_declaration":
            name_node = child.child_by_field_name("name")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                body = child.child_by_field_name("body")
                symbols.append({
                    "name": name,
                    "kind": "Function",
                    "line": child.start_point[0] + 1,
                    "end_line": child.end_point[0] + 1,
                    "docstring": "",
                })
                if body:
                    _extract_calls(body, source_bytes, name, symbols)

        # JavaScript/TS arrow function (const x = () => {})
        elif child.type in ("lexical_declaration", "variable_declaration"):
            # Check for arrow function or function expression
            for decl_child in child.children:
                if decl_child.type == "variable_declarator":
                    name_node = decl_child.child_by_field_name("name")
                    value_node = decl_child.child_by_field_name("value")
                    if name_node and value_node:
                        name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                        if value_node.type in ("arrow_function", "function"):
                            symbols.append({
                                "name": name,
                                "kind": "Function",
                                "line": child.start_point[0] + 1,
                                "end_line": child.end_point[0] + 1,
                                "docstring": "",
                            })
                            body = value_node.child_by_field_name("body")
                            if body:
                                _extract_calls(body, source_bytes, name, symbols)

        # Python class_definition
        elif child.type == "class_definition":
            name_node = child.child_by_field_name("name")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                superclasses = []
                if child.child_by_field_name("superclasses"):
                    super_node = child.child_by_field_name("superclasses")
                    for arg in super_node.children:
                        if arg.type in ("identifier", "attribute"):
                            superclasses.append(source_bytes[arg.start_byte:arg.end_byte].decode("utf-8", errors="replace"))

                symbols.append({
                    "name": name,
                    "kind": "Class",
                    "line": child.start_point[0] + 1,
                    "end_line": child.end_point[0] + 1,
                    "docstring": "",
                    "extends": superclasses,
                })

                body = child.child_by_field_name("body")
                if body:
                    for method in body.children:
                        if method.type == "function_definition":
                            m_name_node = method.child_by_field_name("name")
                            if m_name_node:
                                m_name = source_bytes[m_name_node.start_byte:m_name_node.end_byte].decode("utf-8", errors="replace")
                                m_body = method.child_by_field_name("body")
                                m_docstring = ""
                                if m_body and m_body.children:
                                    first_stmt = m_body.children[0] if m_body.children else None
                                    if first_stmt and first_stmt.type == "expression_statement":
                                        expr = first_stmt.children[0] if first_stmt.children else None
                                        if expr and expr.type == "string":
                                            m_docstring = source_bytes[expr.start_byte:expr.end_byte].decode("utf-8", errors="replace").strip("\"'")

                                symbols.append({
                                    "name": f"{name}.{m_name}",
                                    "kind": "Method",
                                    "line": method.start_point[0] + 1,
                                    "end_line": method.end_point[0] + 1,
                                    "docstring": m_docstring[:200],
                                    "parent": name,
                                })

                                if m_body:
                                    _extract_calls(m_body, source_bytes, f"{name}.{m_name}", symbols)

        # JS/TS method_definition
        elif child.type == "method_definition":
            name_node = child.child_by_field_name("name")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                body = child.child_by_field_name("body")
                symbols.append({
                    "name": name,
                    "kind": "Method",
                    "line": child.start_point[0] + 1,
                    "end_line": child.end_point[0] + 1,
                    "docstring": "",
                })
                if body:
                    _extract_calls(body, source_bytes, name, symbols)

        # JS/TS class_declaration
        elif child.type == "class_declaration":
            name_node = child.child_by_field_name("name")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                symbols.append({
                    "name": name,
                    "kind": "Class",
                    "line": child.start_point[0] + 1,
                    "end_line": child.end_point[0] + 1,
                    "docstring": "",
                })
                body = child.child_by_field_name("body")
                if body:
                    for method in body.children:
                        if method.type == "method_definition":
                            m_name_node = method.child_by_field_name("name")
                            if m_name_node:
                                m_name = source_bytes[m_name_node.start_byte:m_name_node.end_byte].decode("utf-8", errors="replace")
                                m_body = method.child_by_field_name("body")
                                symbols.append({
                                    "name": f"{name}.{m_name}",
                                    "kind": "Method",
                                    "line": method.start_point[0] + 1,
                                    "end_line": method.end_point[0] + 1,
                                    "docstring": "",
                                    "parent": name,
                                })
                                if m_body:
                                    _extract_calls(m_body, source_bytes, f"{name}.{m_name}", symbols)

    return symbols


def _extract_calls(node, source_bytes: bytes, caller: str, symbols: list):
    """Extract function calls within a node and add CALLS relations."""
    for child in node.children:
        if child.type in ("call", "call_expression"):
            func = child.child_by_field_name("function")
            if func:
                if func.type == "identifier":
                    callee = source_bytes[func.start_byte:func.end_byte].decode("utf-8", errors="replace")
                    symbols.append({
                        "_relation": "CALLS",
                        "_caller": caller,
                        "_callee": callee,
                        "line": child.start_point[0] + 1,
                    })
                elif func.type == "attribute":
                    # e.g., self.method()
                    callee = source_bytes[func.start_byte:func.end_byte].decode("utf-8", errors="replace")
                    # Extract just the method name
                    parts = callee.split(".")
                    if len(parts) > 1:
                        symbols.append({
                            "_relation": "CALLS",
                            "_caller": caller,
                            "_callee": parts[-1],
                            "line": child.start_point[0] + 1,
                        })
        # Recurse into child nodes
        _extract_calls(child, source_bytes, caller, symbols)


def parse_file(file_path: Path) -> dict:
    """Parse a source file using Tree-sitter and extract structure.

    Returns:
        dict with imports, symbols, calls, and metadata
    """
    ext = file_path.suffix
    language = _EXTENSION_MAP.get(ext)
    if not language:
        return {"error": f"Unsupported extension: {ext}"}

    try:
        source_bytes = file_path.read_bytes()
    except Exception as e:
        return {"error": f"Cannot read file: {e}"}

    if len(source_bytes) > MAX_FILE_SIZE:
        return {"error": f"File too large: {len(source_bytes)} bytes"}

    try:
        parser = _get_parser(language)
    except Exception:
        return {"error": f"Cannot load parser for {language}"}

    tree = parser.parse(source_bytes)
    root = tree.root_node

    imports = _extract_imports(root, source_bytes)
    symbols = _extract_symbols(root, source_bytes)

    # Separate symbols from calls
    actual_symbols = [s for s in symbols if "_relation" not in s]
    calls = [s for s in symbols if s.get("_relation") == "CALLS"]

    return {
        "language": language,
        "file_path": str(file_path),
        "file_name": file_path.name,
        "file_hash": hashlib.sha256(source_bytes).hexdigest()[:16],
        "file_size": len(source_bytes),
        "imports": imports,
        "symbols": actual_symbols,
        "calls": calls,
        "line_count": source_bytes.count(b"\n") + 1,
    }


# ── Graph Operations ──────────────────────────────────────────────────────

class CodeGraph:
    """Manages the code knowledge graph in LadybugDB."""

    def __init__(self, memory_dir: str | Path | None = None):
        if memory_dir is None:
            memory_dir = Path.home() / ".evol" / "memory"
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._code_graph_path = self.memory_dir / "evol_dd_codigo.lbug"
        self._fallback_path = self.memory_dir / "code_graph.json"
        self._nodes: dict[str, dict] = {}
        self._relations: list[dict] = []
        self._conn = None
        self._init_db()

    def _init_db(self):
        """Initialize LadybugDB or fallback to JSON."""
        if LADYBUG_AVAILABLE:
            try:
                self._conn = lb.connect(str(self._code_graph_path))
                self._conn.execute(
                    "CREATE NODE TABLE IF NOT EXISTS CodeNode("
                    "name STRING PRIMARY KEY, type STRING, properties STRING"
                    ")"
                )
                self._conn.execute(
                    "CREATE REL TABLE IF NOT EXISTS CodeRel("
                    "FROM CodeNode TO CodeNode, relation STRING, metadata STRING"
                    ")"
                )
                return
            except Exception as e:
                print(f"[evol-code-indexer] WARN: LadybugDB failed, using JSON fallback: {e}", file=sys.stderr)

        # JSON fallback
        if self._fallback_path.exists():
            try:
                data = json.loads(self._fallback_path.read_text())
                self._nodes = data.get("nodes", {})
                self._relations = data.get("relations", [])
            except Exception:
                pass

    def _save_fallback(self):
        """Save to JSON fallback."""
        if not LADYBUG_AVAILABLE or self._conn is None:
            self._fallback_path.write_text(json.dumps({
                "nodes": self._nodes,
                "relations": self._relations,
            }, indent=2, ensure_ascii=False))

    def add_node(self, node_type: str, properties: dict) -> str:
        """Add a node to the code graph. Returns node ID."""
        node_id = properties.get("name", hashlib.sha256(json.dumps(properties).encode()).hexdigest()[:12])

        if self._conn:
            props_json = json.dumps(properties, ensure_ascii=False)
            props_b64 = base64.b64encode(props_json.encode()).decode()
            self._conn.execute(
                "MERGE (n:CodeNode {name: $name}) "
                "SET n.type = $type, n.properties = $props",
                parameters={"name": node_id, "type": node_type, "props": props_b64}
            )
            emit_graph_node(project="", node_type=node_type, node_name=node_id, action="created")
        else:
            key = f"{node_type}:{node_id}"
            self._nodes[key] = {"type": node_type, "properties": properties}
            emit_graph_node(project="", node_type=node_type, node_name=node_id, action="created")

        return node_id

    def add_relation(self, source_id: str, relation_type: str, target_id: str,
                     metadata: dict | None = None) -> bool:
        """Add a relation between two nodes."""
        meta = metadata or {}
        meta["created_at"] = datetime.now().isoformat()
        meta_json = json.dumps(meta, ensure_ascii=False)

        if self._conn:
            self._conn.execute(
                "MATCH (a:CodeNode), (b:CodeNode) "
                "WHERE a.name = $src AND b.name = $tgt "
                "CREATE (a)-[:CodeRel {relation: $rel, metadata: $meta}]->(b)",
                parameters={"src": source_id, "tgt": target_id, "rel": relation_type, "meta": meta_json}
            )
            emit_graph_relation(project="", source=source_id, relation=relation_type, target=target_id)
        else:
            self._relations.append({
                "source": source_id,
                "type": relation_type,
                "target": target_id,
                "metadata": meta,
            })
            emit_graph_relation(project="", source=source_id, relation=relation_type, target=target_id)

        return True

    def query_symbol(self, symbol_name: str) -> list[dict]:
        """Query all information about a symbol."""
        results = []

        if self._conn:
            # Find the symbol node
            result = self._conn.execute(
                "MATCH (n:CodeNode) WHERE n.name = $name RETURN n.name, n.type, n.properties",
                parameters={"name": symbol_name}
            )
            for row in result:
                props = {}
                if row[2]:
                    try:
                        props = json.loads(base64.b64decode(row[2]).decode())
                    except Exception:
                        props = {}
                results.append({"name": row[0], "type": row[1], "properties": props})

            # Find outgoing relations (CALLS, IMPORTS, etc.)
            rel_result = self._conn.execute(
                "MATCH (a:CodeNode)-[r:CodeRel]->(b:CodeNode) "
                "WHERE a.name = $name "
                "RETURN a.name, r.relation, b.name",
                parameters={"name": symbol_name}
            )
            for row in rel_result:
                results.append({
                    "relation_from": row[0],
                    "relation_type": row[1],
                    "relation_to": row[2],
                })
        else:
            # JSON fallback
            for key, val in self._nodes.items():
                if symbol_name in key:
                    results.append({"key": key, **val})
            for rel in self._relations:
                if rel["source"] == symbol_name or rel["target"] == symbol_name:
                    results.append(rel)

        return results

    def get_impact(self, symbol_name: str, max_depth: int = 3) -> dict:
        """Analyze impact of changing a symbol (blast radius).

        Returns dict with callers at each depth level.
        """
        impact = {"symbol": symbol_name, "depths": [], "total_affected": 0}

        visited = set()
        current_level = {symbol_name}

        for depth in range(1, max_depth + 1):
            next_level = set()
            callers_at_depth = []

            for sym in current_level:
                # Find all symbols that call this symbol
                if self._conn:
                    result = self._conn.execute(
                        "MATCH (a:CodeNode)-[r:CodeRel]->(b:CodeNode) "
                        "WHERE b.name = $target AND r.relation = 'CALLS' "
                        "RETURN a.name",
                        parameters={"target": sym}
                    )
                    for row in result:
                        caller = row[0]
                        if caller not in visited:
                            callers_at_depth.append(caller)
                            next_level.add(caller)
                else:
                    for rel in self._relations:
                        if rel["target"] == sym and rel["type"] == "CALLS":
                            caller = rel["source"]
                            if caller not in visited:
                                callers_at_depth.append(caller)
                                next_level.add(caller)

            if callers_at_depth:
                impact["depths"].append({
                    "depth": depth,
                    "callers": callers_at_depth,
                    "count": len(callers_at_depth),
                })
                impact["total_affected"] += len(callers_at_depth)

            visited.update(next_level)
            current_level = next_level

            if not next_level:
                break

        return impact

    def get_trace(self, entry_point: str, max_depth: int = 5) -> dict:
        """Trace execution flow from an entry point.

        Returns dict with steps in the execution path.
        """
        trace = {"entry": entry_point, "steps": []}
        visited = set()
        queue = [(entry_point, 0)]

        while queue and len(trace["steps"]) < 50:
            sym, depth = queue.pop(0)
            if sym in visited or depth > max_depth:
                continue
            visited.add(sym)

            trace["steps"].append({"symbol": sym, "depth": depth})

            # Find what this symbol calls
            if self._conn:
                result = self._conn.execute(
                    "MATCH (a:CodeNode)-[r:CodeRel]->(b:CodeNode) "
                    "WHERE a.name = $source AND r.relation = 'CALLS' "
                    "RETURN b.name",
                    parameters={"source": sym}
                )
                for row in result:
                    if row[0] not in visited:
                        queue.append((row[0], depth + 1))
            else:
                for rel in self._relations:
                    if rel["source"] == sym and rel["type"] == "CALLS":
                        if rel["target"] not in visited:
                            queue.append((rel["target"], depth + 1))

        return trace

    def stats(self) -> dict:
        """Get graph statistics."""
        node_count = 0
        rel_count = 0
        node_types = {}
        rel_types = {}

        if self._conn:
            result = self._conn.execute("MATCH (n:CodeNode) RETURN n.type, COUNT(*)")
            for row in result:
                node_types[row[0]] = row[1]
                node_count += row[1]

            result = self._conn.execute("MATCH ()-[r:CodeRel]-() RETURN r.relation, COUNT(*)")
            for row in result:
                rel_types[row[0]] = row[1]
                rel_count += row[1]
        else:
            for key, val in self._nodes.items():
                t = val.get("type", "unknown")
                node_types[t] = node_types.get(t, 0) + 1
                node_count += 1
            for rel in self._relations:
                t = rel.get("type", "unknown")
                rel_types[t] = rel_types.get(t, 0) + 1
                rel_count += 1

        return {
            "total_nodes": node_count,
            "total_relations": rel_count,
            "node_types": node_types,
            "relation_types": rel_types,
        }

    def traverse(self, node_id: str, depth: int = 2) -> dict:
        """BFS traversal from a node. Returns subgraph."""
        nodes = []
        relations = []
        visited = set()

        if self._conn:
            result = self._conn.execute(
                "MATCH (n:CodeNode)-[r:CodeRel*1.." + str(depth) + "]-(m:CodeNode) "
                "WHERE n.name = $start "
                "RETURN DISTINCT m.name, m.type, m.properties",
                parameters={"start": node_id}
            )
            for row in result:
                props = {}
                if row[2]:
                    try:
                        props = json.loads(base64.b64decode(row[2]).decode())
                    except Exception:
                        props = {}
                nodes.append({"name": row[0], "type": row[1], "properties": props})

            rel_result = self._conn.execute(
                "MATCH (a:CodeNode)-[r:CodeRel]->(b:CodeNode) "
                "WHERE a.name = $start "
                "RETURN a.name, r.relation, b.name",
                parameters={"start": node_id}
            )
            for row in rel_result:
                relations.append({"source": row[0], "type": row[1], "target": row[2]})
        else:
            # JSON fallback
            def _traverse(nid: str, d: int):
                if d <= 0 or nid in visited:
                    return
                visited.add(nid)
                # Add the node itself
                for key, val in self._nodes.items():
                    if nid in key:
                        nodes.append({"name": nid, "type": val.get("type", "unknown"), "properties": val.get("properties", {})})
                        break
                # Traverse outgoing relations
                for rel in self._relations:
                    if rel["source"] == nid:
                        relations.append({"source": nid, "type": rel["type"], "target": rel["target"]})
                        _traverse(rel["target"], d - 1)

            _traverse(node_id, depth)

        return {"nodes": nodes, "relations": relations}


# ── Indexer ────────────────────────────────────────────────────────────────

def _get_changed_files(project_root: Path, last_commit: str | None = None) -> list[Path]:
    """Get files changed since last index using git diff."""
    if not last_commit:
        return []

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{last_commit}..HEAD"],
            capture_output=True, text=True, cwd=str(project_root), timeout=30
        )
        if result.returncode != 0:
            return []

        files = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                fpath = project_root / line.strip()
                if fpath.exists() and fpath.suffix in CODE_EXTENSIONS:
                    files.append(fpath)
        return files
    except Exception:
        return []


def _get_current_commit(project_root: Path) -> str | None:
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=str(project_root), timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _get_last_index_commit(project_root: Path) -> str | None:
    """Read last indexed commit from marker file."""
    marker = project_root / LAST_INDEX_MARKER
    if marker.exists():
        return marker.read_text().strip()
    return None


def _save_last_index_commit(project_root: Path, commit: str):
    """Save last indexed commit to marker file."""
    marker = project_root / LAST_INDEX_MARKER
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(commit)


def index_project(project_root: Path, incremental: bool = True, graph: CodeGraph | None = None) -> dict:
    """Index all code files in a project.

    Args:
        project_root: Root directory of the project
        incremental: If True, only index changed files since last index
        graph: CodeGraph instance (creates new if None)

    Returns:
        Stats dict with counts
    """
    if graph is None:
        graph = CodeGraph()

    stats = {"files_indexed": 0, "symbols_found": 0, "relations_found": 0, "errors": 0}

    # Determine files to index
    if incremental:
        last_commit = _get_last_index_commit(project_root)
        if last_commit:
            files = _get_changed_files(project_root, last_commit)
            if files:
                print(f"[evol-code-indexer] Incremental: {len(files)} files changed since {last_commit[:8]}")
            else:
                print("[evol-code-indexer] No changes detected. Use --full for full re-index.")
                return stats
        else:
            # No previous index, do full
            files = None
    else:
        files = None

    if files is None:
        # Full index
        files = []
        for ext in CODE_EXTENSIONS:
            files.extend(project_root.rglob(f"*{ext}"))

        # Filter out skip dirs
        filtered = []
        for f in files:
            parts = f.relative_to(project_root).parts
            if not any(skip in parts for skip in SKIP_DIRS):
                filtered.append(f)
        files = filtered
        print(f"[evol-code-indexer] Full index: {len(files)} files")

    # Index each file
    for file_path in files:
        try:
            result = parse_file(file_path)
            if "error" in result:
                stats["errors"] += 1
                continue

            rel_path = str(file_path.relative_to(project_root))

            # Add File node
            file_node_id = graph.add_node("File", {
                "name": rel_path,
                "path": rel_path,
                "language": result["language"],
                "hash": result["file_hash"],
                "size": result["file_size"],
                "line_count": result["line_count"],
            })

            # Add Module node for the file
            module_name = file_path.stem
            graph.add_node("Module", {
                "name": module_name,
                "path": rel_path,
                "language": result["language"],
            })

            # Add CONTAINS relation
            graph.add_relation(file_node_id, "CONTAINS", module_name)

            # Add Symbol nodes and relations
            for sym in result["symbols"]:
                sym_id = sym["name"]
                graph.add_node("Symbol", {
                    "name": sym["name"],
                    "kind": sym["kind"],
                    "line": sym["line"],
                    "end_line": sym.get("end_line"),
                    "docstring": sym.get("docstring", ""),
                    "parent": sym.get("parent"),
                    "file": rel_path,
                })

                # File CONTAINS Symbol
                graph.add_relation(file_node_id, "CONTAINS", sym_id)

                # Module EXPORTS Symbol
                graph.add_relation(module_name, "EXPORTS", sym_id)

                # EXTENDS relation for classes
                if sym.get("extends"):
                    for ext_class in sym["extends"]:
                        graph.add_node("Symbol", {"name": ext_class, "kind": "Class"})
                        graph.add_relation(sym_id, "EXTENDS", ext_class)

                stats["symbols_found"] += 1

            # Add IMPORTS relations
            for imp in result["imports"]:
                graph.add_relation(file_node_id, "IMPORTS", imp["module"])
                stats["relations_found"] += 1

            # Add CALLS relations
            for call in result["calls"]:
                graph.add_relation(call["_caller"], "CALLS", call["_callee"], {
                    "line": call.get("line"),
                })
                stats["relations_found"] += 1

            stats["files_indexed"] += 1

        except Exception as e:
            print(f"[evol-code-indexer] ERROR indexing {file_path}: {e}", file=sys.stderr)
            stats["errors"] += 1

    # Save last index commit
    current_commit = _get_current_commit(project_root)
    if current_commit:
        _save_last_index_commit(project_root, current_commit)

    graph._save_fallback()

    return stats


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Evol-DD Code Graph Indexer (Tree-sitter)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # index
    idx = sub.add_parser("index", help="Index code files")
    idx.add_argument("path", nargs="?", default=".", help="Project root path")
    idx.add_argument("--full", action="store_true", help="Force full re-index")
    idx.add_argument("--memory-dir", help="Memory directory path")

    # query
    qry = sub.add_parser("query", help="Query a symbol")
    qry.add_argument("symbol", help="Symbol name to query")

    # graph
    grp = sub.add_parser("graph", help="Show dependency graph for a symbol")
    grp.add_argument("symbol", help="Symbol name")
    grp.add_argument("--depth", type=int, default=2, help="Traversal depth")

    # impact
    imp = sub.add_parser("impact", help="Analyze blast radius")
    imp.add_argument("symbol", help="Symbol name")
    imp.add_argument("--max-depth", type=int, default=3, help="Max depth")

    # trace
    trc = sub.add_parser("trace", help="Trace execution flow")
    trc.add_argument("entry", help="Entry point symbol")
    trc.add_argument("--max-depth", type=int, default=5, help="Max depth")

    # stats
    sub.add_parser("stats", help="Show graph statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    graph = CodeGraph(getattr(args, "memory_dir", None))

    if args.command == "index":
        project_root = Path(args.path).resolve()
        if not project_root.is_dir():
            print(f"[evol-code-indexer] ERROR: {project_root} is not a directory", file=sys.stderr)
            sys.exit(1)

        print(f"[evol-code-indexer] Indexing: {project_root}")
        stats = index_project(project_root, incremental=not args.full, graph=graph)
        print(f"\n[evol-code-indexer] Done:")
        print(f"  Files indexed: {stats['files_indexed']}")
        print(f"  Symbols found: {stats['symbols_found']}")
        print(f"  Relations found: {stats['relations_found']}")
        print(f"  Errors: {stats['errors']}")

    elif args.command == "query":
        results = graph.query_symbol(args.symbol)
        if results:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"[evol-code-indexer] Symbol not found: {args.symbol}")

    elif args.command == "graph":
        result = graph.traverse(args.symbol, depth=args.depth)
        if result["nodes"] or result["relations"]:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"[evol-code-indexer] No graph found for: {args.symbol}")

    elif args.command == "impact":
        result = graph.get_impact(args.symbol, max_depth=args.max_depth)
        print(f"\nImpact Analysis: {args.symbol}")
        print("=" * 40)
        if result["depths"]:
            for d in result["depths"]:
                print(f"\nDepth {d['depth']}: {d['count']} caller(s)")
                for caller in d["callers"]:
                    print(f"  - {caller}")
            print(f"\nTotal affected: {result['total_affected']} symbol(s)")
        else:
            print("No callers found.")

    elif args.command == "trace":
        result = graph.get_trace(args.entry, max_depth=args.max_depth)
        print(f"\nExecution Trace: {args.entry}")
        print("=" * 40)
        if result["steps"]:
            for i, step in enumerate(result["steps"], 1):
                indent = "  " * step["depth"]
                print(f"{i}. {indent}{step['symbol']}")
        else:
            print("No trace found.")

    elif args.command == "stats":
        stats = graph.stats()
        print(f"\nCode Graph Statistics")
        print("=" * 40)
        print(f"Total nodes: {stats['total_nodes']}")
        print(f"Total relations: {stats['total_relations']}")
        if stats["node_types"]:
            print("\nNode types:")
            for t, count in sorted(stats["node_types"].items(), key=lambda x: -x[1]):
                print(f"  {t}: {count}")
        if stats["relation_types"]:
            print("\nRelation types:")
            for t, count in sorted(stats["relation_types"].items(), key=lambda x: -x[1]):
                print(f"  {t}: {count}")


if __name__ == "__main__":
    main()
