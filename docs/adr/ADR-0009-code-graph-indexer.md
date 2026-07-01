# ADR-0009: Code Graph Indexer Architecture

**Status:** Accepted  
**Date:** 2026-06-07  
**Deciders:** evol-architect, evol-builder  
**Technical story:** Evol-DD needs code awareness for impact analysis, process tracing, and safe refactoring.

---

## Context

Evol-DD operates on codebases but previously had no structured understanding of code relationships. When refactoring, agents couldn't determine blast radius. When reviewing, they couldn't trace execution paths. When debugging, they couldn't follow call chains.

We needed a code graph indexer that:
1. Parses code into structured symbols (functions, classes, modules)
2. Maps relationships (calls, imports, extends)
3. Supports impact analysis and process tracing
4. Integrates with the existing EDMS infrastructure

---

## Decision

### Chose Tree-sitter (mandatory, no fallback)

**Options considered:**
1. **Tree-sitter** — Fast, incremental parsing, supports Python/JS/TS, WASM-based
2. **Regex-based parsing** — Simple but fragile, misses edge cases
3. **AST-based (language-specific)** — Accurate but requires per-language implementations
4. **External tool (LSP)** — Rich information but heavyweight, requires running language servers

**Why Tree-sitter:**
- Mandatory parsing (no regex fallback) ensures accuracy
- Single implementation handles Python, JavaScript, TypeScript
- Incremental parsing aligns with git-diff-based incremental indexing
- Fast enough for real-time use in hooks and workflows

### Chose separate LadybugDB instance

**Options considered:**
1. **Separate `evol_dd_codigo.lbug`** — Independent evolution, no schema conflicts
2. **Same `evol_dd_memoria.lbug`** — Simpler but couples knowledge and code graphs
3. **Shared graph with node types** — Flexible but complicates queries

**Why separate:**
- Code graph and knowledge graph evolve independently
- Schema is fundamentally different (CodeNode vs MemoryNode)
- Enables specialized queries without polluting knowledge graph
- Cleaner backup/restore semantics

### Chose JSON fallback

**Options considered:**
1. **JSON fallback (`code_graph.json`)** — Works without LadybugDB
2. **Fail if LadybugDB unavailable** — Cleaner but blocks users without LadybugDB
3. **SQLite fallback** — More structured but adds dependency

**Why JSON:**
- Zero additional dependencies
- Human-readable for debugging
- Enables stdlib-only operation
- Consistent with knowledge graph fallback pattern

---

## Consequences

### Positive
- Impact analysis prevents unsafe refactoring
- Process tracing aids debugging and code review
- Incremental indexing keeps graph fresh with minimal overhead
- Separate graph enables independent evolution

### Negative
- Tree-sitter adds ~50MB to dependencies (optional `[code]` extra)
- Separate LadybugDB instance means two graph databases to maintain
- JSON fallback is slower than native LadybugDB for large codebases

### Mitigations
- Tree-sitter is optional via `pip install evol-dd[code]`
- LadybugDB API mismatch handled via JSON fallback (graceful degradation)
- Incremental indexing keeps update time < 5s for typical changes

---

## References

- `scripts/evol_code_indexer.py` — Core implementation
- `tests/test_code_indexer.py` — 11 tests
- `tests/test_impact.py` — 6 tests
- `skills/code-indexer/SKILL.md` — User-facing skill
- `.agent/workflows/code-indexer.md` — Workflow documentation
