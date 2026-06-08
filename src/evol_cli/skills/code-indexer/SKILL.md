---
name: code-indexer
description: Tree-sitter code graph indexing for impact analysis, process tracing, and incremental git-based updates. Separate LadybugDB instance for code symbols.
category: code-analysis
trigger: /code-index
---

# code-indexer

## Philosophy
Code awareness is fundamental to safe refactoring, impact analysis, and process tracing. The code graph indexer uses Tree-sitter (mandatory) to parse code into a structured graph stored in a separate LadybugDB instance (`evol_dd_codigo.lbug`).

## Features
- **Tree-sitter parsing**: Python, JavaScript, TypeScript (mandatory, no regex fallback)
- **Code graph nodes**: File, Module, Symbol (Function/Class/Method), Test, Commit, Branch
- **Code graph relations**: IMPORTS, CALLS, EXTENDS, CONTAINS, EXPORTS, TESTS, MODIFIES, BLAME
- **Impact analysis**: Direct/indirect callers, blast radius computation
- **Process tracing**: Follow execution paths from entry points
- **Incremental indexing**: Git diff-based updates via `git diff --name-only $LAST_COMMIT..HEAD`
- **Separate graph**: Independent from knowledge graph (`evol_dd_memoria.lbug`)

## When to Use
- Before refactoring to understand blast radius
- During code review to trace impact of changes
- When onboarding to understand codebase structure
- After implementing features to update the code graph
- When debugging to trace execution paths

## Commands

### Full Project Index
```bash
python3 scripts/evol_code_indexer.py index
```

### Incremental Index (Git Diff)
```bash
python3 scripts/evol_code_indexer.py incremental
```

### Impact Analysis
```bash
python3 scripts/evol_code_indexer.py impact <SymbolName> --depth=3
```

### Process Tracing
```bash
python3 scripts/evol_code_indexer.py trace <EntryPoint> --max-depth=5
```

### Symbol Query
```bash
python3 scripts/evol_code_indexer.py query <Pattern>
```

### Stats
```bash
python3 scripts/evol_code_indexer.py stats
```

## Via EDMS Orchestrator
```bash
edms-code-index          # Full project index
edms-code-impact <Sym>   # Impact analysis
edms-code-trace <Entry>  # Process tracing
edms-code-query <Pat>    # Symbol search
edms-code-stats          # Code graph statistics
```

## Reference
- `scripts/evol_code_indexer.py` — Core implementation (1000+ lines)
- `scripts/evol_memory_store.py` — `code_impact()`, `code_trace()`, `code_query()`, `code_stats()`
- `tests/test_code_indexer.py` — 11 tests
- `tests/test_impact.py` — 6 tests
- `docs/adr/ADR-0009-code-graph-indexer.md` — Architecture decision
