#!/usr/bin/env python3
"""Evol-DD Memory Engine — Conversational memory + EDMS (ChromaDB/LadybugDB)."""
import os, sys, json, time, argparse, re
from datetime import datetime, timedelta
from pathlib import Path
from _evol_common import get_logger, get_provider

logger = get_logger("memory")

MEMORY_DIR = "memory"
AGENT_MEMORY_FILE = "AGENT_MEMORY.md"
DIALOG_DIR = "dialog"
TOOL_RESULT_DIR = "tool_result"
COMPACT_THRESHOLD = int(os.environ.get("EVOL_MEMORY_COMPACT_THRESHOLD", 90000))
COMPACT_RESERVE = int(os.environ.get("EVOL_MEMORY_COMPACT_RESERVE", 10000))
TOOL_TTL_DAYS = int(os.environ.get("EVOL_MEMORY_TOOL_TTL_DAYS", 3))

# ── EDMS integration ──────────────────────────────────────────────────────────

def _get_store():
    """Lazy import of MemoryStore with fallback."""
    try:
        from evol_memory_store import MemoryStore
        return MemoryStore()
    except ImportError:
        return None

def load():
    """Load session context (SessionStart hook)."""
    print("=== Memory Load ===")

    if os.path.exists(AGENT_MEMORY_FILE):
        print("--- AGENT_MEMORY.md ---")
        with open(AGENT_MEMORY_FILE) as f:
            print(f.read())

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    journal_path = os.path.join(MEMORY_DIR, f"{yesterday}.md")

    if os.path.exists(journal_path):
        print(f"--- Journal: {yesterday} ---")
        with open(journal_path) as f:
            print(f.read())

    print("===================")

def summarize(messages_file=None):
    """Persist session to journal (Stop hook)."""
    today = datetime.now().strftime("%Y-%m-%d")
    journal_path = os.path.join(MEMORY_DIR, f"{today}.md")

    os.makedirs(MEMORY_DIR, exist_ok=True)

    messages = []
    if messages_file and os.path.exists(messages_file):
        with open(messages_file) as f:
            for line in f:
                messages.append(json.loads(line))

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    entry = f"""
## Sesion {timestamp}

### Factual Memory
- Date: {today}
- Session duration: {len(messages)} messages
- Active project: See memoria.md

### Reflections & Logic
[Session summary extracted]

"""

    if os.path.exists(journal_path):
        with open(journal_path, "a") as f:
            f.write(entry)
    else:
        with open(journal_path, "w") as f:
            f.write(f"# {today}\n{entry}")

    total_tokens = sum(len(m.get("content", "")) for m in messages)
    if total_tokens > COMPACT_THRESHOLD:
        compact(messages_file)

    print(f"[OK] Session persisted to {journal_path}")

def compact(messages_file=None):
    """Compact long history into structured summary."""
    if not messages_file or not os.path.exists(messages_file):
        return

    provider = get_provider()

    messages = []
    with open(messages_file) as f:
        for line in f:
            messages.append(json.loads(line))

    truncated = messages[-100:]

    summary_prompt = f"Summarize this session into structured format:\nGoal:\nProgress:\nKey Decisions:\nNext Steps:\nCritical Context:"

    if provider.__class__.__name__ == "MockProvider":
        summary = "[mock summary — requires real LLM for actual summarization]"
    else:
        result = provider.complete(summary_prompt, max_tokens=500)
        summary = result["content"]

    with open(AGENT_MEMORY_FILE, "w") as f:
        f.write(f"# Agent Memory\n\n## Last Compact: {datetime.now().isoformat()}\n\n{summary}\n")

    print(f"[OK] Memory compacted to {AGENT_MEMORY_FILE}")

def search(query, max_results=5):
    """BM25-style search over memory."""
    results = []

    if os.path.exists(AGENT_MEMORY_FILE):
        with open(AGENT_MEMORY_FILE) as f:
            content = f.read()
            if query.lower() in content.lower():
                results.append(("AGENT_MEMORY.md", content[:200]))

    for journal in sorted(Path(MEMORY_DIR).glob("*.md")):
        with open(journal) as f:
            content = f.read()
            if query.lower() in content.lower():
                results.append((str(journal), content[:200]))

    for i, (source, snippet) in enumerate(results[:max_results]):
        print(f"[{i+1}] {source}")
        print(f"    {snippet[:100]}...")

    print(f"[INFO] Found {len(results)} results")

def gc(days=None):
    """Purge expired tool results."""
    if days is None:
        days = TOOL_TTL_DAYS

    cutoff = datetime.now() - timedelta(days=days)
    removed = 0

    if os.path.exists(TOOL_RESULT_DIR):
        for f in os.listdir(TOOL_RESULT_DIR):
            path = os.path.join(TOOL_RESULT_DIR, f)
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                os.remove(path)
                removed += 1

    print(f"[GC] Removed {removed} expired tool results")

def stats():
    """Show memory system stats."""
    print("=== Memory Stats ===")

    journal_count = len(list(Path(MEMORY_DIR).glob("*.md")))
    print(f"Journals: {journal_count}")

    if os.path.exists(AGENT_MEMORY_FILE):
        size = os.path.getsize(AGENT_MEMORY_FILE)
        print(f"AGENT_MEMORY.md: {size} bytes")
    else:
        print("AGENT_MEMORY.md: not found")

    dialog_count = len(list(Path(DIALOG_DIR).glob("*.jsonl")))
    print(f"Dialog files: {dialog_count}")

    if os.path.exists(TOOL_RESULT_DIR):
        tool_count = len(os.listdir(TOOL_RESULT_DIR))
        print(f"Tool results: {tool_count}")

    print("===================")

def _sprint_num_str(sprint) -> str:
    """Normaliza sprint a 2 dígitos: 1 → '01', '3' → '03', '12' → '12'."""
    return f"{int(sprint):02d}"


def _update_lecciones_index(index_path: Path, sprint: str, today: str) -> None:
    entry = f"| sprint-{sprint} | [sprint-{sprint}.md](sprint-{sprint}.md) | {today} |"
    header = (
        "# INDEX — Lecciones por Sprint\n\n"
        "> Indice de lecciones separadas por sprint. Categorias: ARQUITECTURA, SEGURIDAD, DOMINIO, TESTING, DEVOPS, PROCESO, HERRAMIENTAS.\n\n"
        "| Sprint | Archivo | Fecha cierre |\n"
        "|--------|---------|-------------|\n"
    )
    if not index_path.exists():
        index_path.write_text(header + entry + "\n", encoding="utf-8")
        return
    content = index_path.read_text(encoding="utf-8")
    marker = f"| sprint-{sprint} |"
    if marker in content:
        lines = [entry if l.startswith(marker) else l for l in content.splitlines()]
        index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        index_path.write_text(content.rstrip("\n") + "\n" + entry + "\n", encoding="utf-8")


def sprint_close(sprint, project=".", memoria_content=None, lecciones_content=None, force=False):
    """Cierra sprint: crea acuerdos/memoria/sprint-NN.md + acuerdos/lecciones/sprint-NN.md."""
    s = _sprint_num_str(sprint)
    today = datetime.now().strftime("%Y-%m-%d")
    acuerdos = Path(project) / "acuerdos"
    mem_dir = acuerdos / "memoria"
    les_dir = acuerdos / "lecciones"
    mem_dir.mkdir(parents=True, exist_ok=True)
    les_dir.mkdir(parents=True, exist_ok=True)

    sprint_mem = mem_dir / f"sprint-{s}.md"
    sprint_les = les_dir / f"sprint-{s}.md"

    if sprint_mem.exists() and not force:
        print(f"[evol-memory] acuerdos/memoria/sprint-{s}.md ya existe. Usar --force para sobreescribir.")
    else:
        content = memoria_content or f"# Memoria Sprint {s} — {today}\n\n## Hitos\n\n-\n\n## Bloqueos\n\n-\n\n## Proxima sesion\n\n-\n"
        sprint_mem.write_text(content, encoding="utf-8")
        print(f"[evol-memory] ✓ acuerdos/memoria/sprint-{s}.md creado.")

    if sprint_les.exists() and not force:
        print(f"[evol-memory] acuerdos/lecciones/sprint-{s}.md ya existe. Usar --force para sobreescribir.")
    else:
        content = lecciones_content or f"# Lecciones Sprint {s} — {today}\n\n> Formato: CATEGORIA / Contexto / Problema / Causa raiz / Leccion / Aplica a.\n\n"
        sprint_les.write_text(content, encoding="utf-8")
        print(f"[evol-memory] ✓ acuerdos/lecciones/sprint-{s}.md creado.")

    _update_lecciones_index(les_dir / "INDEX.md", s, today)
    print(f"[evol-memory] ✓ acuerdos/lecciones/INDEX.md actualizado.")

    # Update knowledge graph with sprint node
    store = _get_store()
    if store:
        project_name = Path(project).resolve().name
        sprint_id = f"sprint-{s}"

        # Add sprint node
        store.graph_add_node("Sprint", {
            "number": s,
            "status": "closed",
            "fecha_cierre": today,
        })

        # Add relations
        store.graph_add_relation(project_name, "TIENE", sprint_id)

        # Index sprint files into EDMS
        if sprint_mem.exists():
            content = sprint_mem.read_text(encoding="utf-8")
            if len(content.strip()) > 20:
                store.index(content, {
                    "proyecto": project_name,
                    "tipo": "resumen",
                    "fase": "Retro",
                    "sprint": s,
                })

        if sprint_les.exists():
            content = sprint_les.read_text(encoding="utf-8")
            if len(content.strip()) > 20:
                store.index(content, {
                    "proyecto": project_name,
                    "tipo": "leccion",
                    "fase": "QA",
                    "sprint": s,
                })

        print(f"[evol-memory] ✓ Grafo actualizado: {sprint_id}")

    # MEMORY.md atomico: 3 atomos + agregado generado (ADR atomicidad)
    _ensure_memory_atoms(mem_dir)
    _regen_memory_aggregate(mem_dir)
    print("[evol-memory] ✓ acuerdos/memoria/ atomos (decisiones/convenciones/riesgos) + MEMORY.md regenerado.")

    # Compliance: verify lessons + generate report
    compliance_script = Path(project) / "scripts" / "evol-compliance.py"
    lessons_script = Path(project) / "scripts" / "evol-lessons.py"
    if compliance_script.exists():
        import subprocess
        print(f"[evol-memory] Verificando compliance del sprint {s}...")
        try:
            subprocess.run(
                [sys.executable, str(lessons_script), "verify-applied", "--sprint", str(s)],
                cwd=str(project), capture_output=True, timeout=30
            )
            subprocess.run(
                [sys.executable, str(compliance_script), "report", "--sprint", str(s)],
                cwd=str(project), capture_output=True, timeout=30
            )
            report_path = acuerdos / "auditoria" / f"compliance-sprint-{s}.md"
            if report_path.exists():
                print(f"[evol-memory] ✓ Compliance report: {report_path}")
        except Exception as e:
            print(f"[evol-memory] WARN: Compliance report failed: {e}")


# ── MEMORY.md atomico ──────────────────────────────────────────────────────────

_MEMORY_ATOMS = {
    "decisiones.md": ("Decisiones clave", "Decisiones de arquitectura y producto persistentes."),
    "convenciones.md": ("Convenciones", "Estandares de codigo y patrones del proyecto."),
    "riesgos.md": ("Riesgos activos", "Riesgos vigentes y mitigaciones."),
}


def _ensure_memory_atoms(mem_dir):
    mem_dir.mkdir(parents=True, exist_ok=True)
    for fname, (titulo, desc) in _MEMORY_ATOMS.items():
        atom = mem_dir / fname
        if not atom.exists():
            atom.write_text(f"# {titulo}\n\n> Atomo de MEMORY. {desc}\n\n-\n", encoding="utf-8")


def _regen_memory_aggregate(mem_dir):
    parts = [
        "# MEMORY.md — Hechos persistentes del proyecto",
        "",
        "> GENERADO automaticamente desde los atomos (decisiones/convenciones/riesgos).",
        "> NO editar este archivo: editar el atomo correspondiente y regenerar via",
        "> `evol-memory sprint-close` o `evol-memory memory-split`.",
        "",
    ]
    for fname in _MEMORY_ATOMS:
        atom = mem_dir / fname
        if atom.exists():
            parts.append(atom.read_text(encoding="utf-8").rstrip())
            parts.append("")
    (mem_dir / "MEMORY.md").write_text("\n".join(parts) + "\n", encoding="utf-8")


def memory_split(project="."):
    """Migra MEMORY.md monolitico legacy a 3 atomos (idempotente)."""
    mem_dir = Path(project) / "acuerdos" / "memoria"
    memory_md = mem_dir / "MEMORY.md"
    _ensure_memory_atoms(mem_dir)
    if memory_md.exists():
        content = memory_md.read_text(encoding="utf-8")
        section_map = {
            "decisiones.md": r"(?is)##\s*decisiones[^\n]*\n(.*?)(?=^##\s|\Z)",
            "convenciones.md": r"(?is)##\s*convenciones[^\n]*\n(.*?)(?=^##\s|\Z)",
            "riesgos.md": r"(?is)##\s*riesgos[^\n]*\n(.*?)(?=^##\s|\Z)",
        }
        if "GENERADO automaticamente" not in content:
            for fname, pattern in section_map.items():
                m = re.search(pattern, content, re.MULTILINE)
                if m and m.group(1).strip() and m.group(1).strip() != "-":
                    titulo, desc = _MEMORY_ATOMS[fname]
                    (mem_dir / fname).write_text(
                        f"# {titulo}\n\n> Atomo de MEMORY. {desc}\n\n{m.group(1).strip()}\n",
                        encoding="utf-8",
                    )
                    print(f"[evol-memory] migrado seccion -> {fname}")
    _regen_memory_aggregate(mem_dir)
    print("[evol-memory] ✓ MEMORY.md migrado a 3 atomos + agregado regenerado.")


# ── EDMS subcommands ──────────────────────────────────────────────────────────

def edms_index(text, project=".", sprint=None, phase=None, tipo="artefacto",
               disciplinas=None, agent=None, importance=0.5):
    """Index text into EDMS (ChromaDB + LadybugDB)."""
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible. Instalar: pip install -e '.[memory]'")
        return

    meta = {
        "proyecto": Path(project).resolve().name,
        "tipo": tipo,
        "importance": importance,
        "source_file": None,
    }
    if sprint:
        meta["sprint"] = sprint
    if phase:
        meta["fase"] = phase
    if disciplinas:
        meta["disciplinas"] = [d.strip() for d in disciplinas.split(",")]
    if agent:
        meta["agente"] = agent

    doc_id = store.index(text, meta)
    print(f"[evol-memory] Indexed: {doc_id} (tipo={tipo})")


def edms_search(query, project=".", sprint=None, phase=None, tipo=None,
                disciplinas=None, n_results=10):
    """Search EDMS with metadata filters."""
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible.")
        return

    results = store.search(
        query,
        project=Path(project).resolve().name,
        sprint=sprint,
        phase=phase,
        tipo=tipo,
        disciplinas=disciplinas,
        n_results=n_results,
    )

    if not results:
        print("[evol-memory] No results found.")
        return

    for i, r in enumerate(results):
        meta = r.get("metadata", {})
        print(f"[{i+1}] {r['id']} (distance={r.get('distance', '?'):.3f})")
        print(f"    tipo={meta.get('tipo', '?')} sprint={meta.get('sprint', '?')} fase={meta.get('fase', '?')}")
        print(f"    {r['text'][:120]}...")
    print(f"[evol-memory] {len(results)} results")


def edms_wake_up(project=".", sprint=None):
    """Generate wake-up context for new session."""
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible.")
        return

    ctx = store.get_context(Path(project).resolve().name, sprint=sprint)
    print(ctx)


def edms_graph_add_node(node_type, props_json):
    """Add node to knowledge graph."""
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible.")
        return

    try:
        props = json.loads(props_json)
    except json.JSONDecodeError:
        print("[evol-memory] Error: props_json must be valid JSON")
        return

    node_id = store.graph_add_node(node_type, props)
    print(f"[evol-memory] Node created: {node_type}:{node_id}")


def edms_graph_add_relation(source_id, relation_type, target_id):
    """Add relation to knowledge graph."""
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible.")
        return

    store.graph_add_relation(source_id, relation_type, target_id)
    print(f"[evol-memory] Relation: {source_id} -[{relation_type}]-> {target_id}")


def edms_graph_traverse(node_id, depth=2):
    """Traverse knowledge graph from a node."""
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible.")
        return

    result = store.graph_traverse(node_id, depth)
    if result.get("relations"):
        print(f"[evol-memory] Subgraph from {node_id}:")
        for rel in result["relations"]:
            print(f"  {rel['source']} -[{rel['type']}]-> {rel['target']}")
    else:
        print(f"[evol-memory] No connections found for {node_id}")


def edms_bootstrap(project="."):
    """Import existing project state into EDMS (idempotent).

    Detects and imports:
    1. acuerdos/**/*.md (existing documentation)
    2. Legacy memory files (memoria.md, lecciones.md, AGENT_MEMORY.md)
    3. Git history (recent commits, branches, tags)
    4. Project metadata (pyproject.toml, package.json, etc.)
    5. Graph nodes (Proyecto, Disciplinas, Sprints)
    """
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible.")
        return

    project_path = Path(project).resolve()
    project_name = project_path.name
    stats = {'acuerdos': 0, 'legacy': 0, 'git': 0, 'graph': 0}

    # 1. Create Proyecto node in graph
    store.graph_add_node("Proyecto", {
        "name": project_name,
        "path": str(project_path),
        "bootstrapped_at": datetime.now().isoformat(),
    })
    stats['graph'] += 1

    # 2. Import acuerdos/**/*.md
    acuerdos = project_path / "acuerdos"
    if acuerdos.exists():
        for md_file in sorted(acuerdos.rglob("*.md")):
            if md_file.name == "README.md":
                continue

            content = md_file.read_text(encoding="utf-8")
            if len(content.strip()) < 20:
                continue

            rel = md_file.relative_to(acuerdos)
            parts = rel.parts

            meta = {"proyecto": project_name, "source_file": str(rel)}

            if "memoria" in parts:
                meta["tipo"] = "decision"
                meta["fase"] = "Retro"
            elif "lecciones" in parts:
                meta["tipo"] = "leccion"
                meta["fase"] = "QA"
            elif "research" in parts:
                meta["tipo"] = "artefacto"
                meta["fase"] = "Spec"
            elif "discovery" in parts:
                meta["tipo"] = "artefacto"
                meta["fase"] = "Briefing"
            else:
                meta["tipo"] = "artefacto"

            store.index(content, meta)
            stats['acuerdos'] += 1

    # 3. Import legacy memory files
    legacy_files = {
        'memoria.md': ('decision', 'Retro'),
        'lecciones.md': ('leccion', 'QA'),
        'AGENT_MEMORY.md': ('resumen', 'Retro'),
    }

    for filename, (tipo, fase) in legacy_files.items():
        legacy_path = project_path / filename
        if legacy_path.exists():
            content = legacy_path.read_text(encoding="utf-8")
            if len(content.strip()) > 20:
                # Split by sections if file is large
                sections = content.split('\n## ')
                for i, section in enumerate(sections):
                    if i == 0 and not section.strip().startswith('#'):
                        section = '# ' + section
                    if len(section.strip()) > 20:
                        meta = {
                            "proyecto": project_name,
                            "tipo": tipo,
                            "fase": fase,
                            "source_file": filename,
                            "section_index": i,
                        }
                        store.index(section, meta)
                        stats['legacy'] += 1

    # 4. Import git history (recent commits)
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'log', '--oneline', '-20', '--format=%h|%s|%ad', '--date=short'],
            capture_output=True, text=True, cwd=str(project_path), timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|', 2)
                    if len(parts) >= 2:
                        commit_hash, message = parts[0], parts[1]
                        meta = {
                            "proyecto": project_name,
                            "tipo": "artefacto",
                            "fase": "Build",
                            "source_file": f"git:{commit_hash}",
                            "commit_hash": commit_hash,
                        }
                        store.index(f"Commit {commit_hash}: {message}", meta)
                        stats['git'] += 1

        # Import branches
        result = subprocess.run(
            ['git', 'branch', '-a', '--format=%(refname:short)'],
            capture_output=True, text=True, cwd=str(project_path), timeout=5
        )
        if result.returncode == 0:
            for branch in result.stdout.strip().split('\n'):
                branch = branch.strip()
                if branch and not branch.startswith('origin/'):
                    store.graph_add_node("Branch", {"name": branch})
                    store.graph_add_relation(project_name, "TIENE", branch)
                    stats['graph'] += 1
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass  # Git not available or too slow

    # 5. Detect disciplines from project files
    disciplines_map = {
        'pyproject.toml': 'DDD',
        'package.json': 'DDD',
        'Dockerfile': 'DevDD',
        'docker-compose.yml': 'DevDD',
        '.github/workflows': 'DevDD',
        'tests/': 'TDD',
        'docs/': 'DocDD',
        'SECURITY.md': 'SecDD',
        'openapi': 'APIDD',
    }

    for pattern, discipline in disciplines_map.items():
        matches = list(project_path.rglob(pattern))
        if matches:
            store.graph_add_node("Disciplina", {"name": discipline})
            store.graph_add_relation(project_name, "DEFINE", discipline)
            stats['graph'] += 1

    # 6. Create Sprint nodes for existing sprints
    sprints_dir = acuerdos / "sprints"
    if sprints_dir.exists():
        for sprint_file in sprints_dir.glob("sprint-*.md"):
            sprint_num = sprint_file.stem.replace("sprint-", "")
            store.graph_add_node("Sprint", {"number": sprint_num, "status": "closed"})
            store.graph_add_relation(project_name, "TIENE", f"sprint-{sprint_num}")
            stats['graph'] += 1

    # Summary
    total = sum(stats.values())
    print(f"[evol-memory] ✓ Bootstrap completado: {total} items")
    print(f"  acuerdos: {stats['acuerdos']}, legacy: {stats['legacy']}, "
          f"git: {stats['git']}, graph: {stats['graph']}")


def edms_stats():
    """Show EDMS stats."""
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible.")
        return

    print("=== EDMS Stats ===")
    print(f"Memory dir: {store.memory_dir}")

    # ChromaDB stats
    if store._chroma_collection:
        count = store._chroma_collection.count()
        print(f"ChromaDB collection 'evol_memory': {count} drawers")
    else:
        print("ChromaDB: not available (using local fallback)")

    # Local fallback stats
    idx_file = store.memory_dir / "local_index.json"
    if idx_file.exists():
        with open(idx_file) as f:
            local_count = len(json.load(f))
        print(f"Local index: {local_count} drawers")

    # Graph stats
    if store._ladybug_client if hasattr(store, '_ladybug_client') else False:
        print("LadybugDB: available")
    else:
        print(f"Graph (in-memory): {len(store._graph)} entries")

    print("====================")


# ── 4-Tier Consolidation commands ─────────────────────────────────────────────

def edms_consolidate(from_tier, to_tier, project=".", max_items=50):
    """Consolidate drawers from one tier to the next."""
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible.")
        return

    count = store.consolidate_tier(from_tier, to_tier, project, max_items)
    print(f"[evol-memory] Consolidated {count} items: {from_tier} -> {to_tier}")


def edms_decay(project=".", days=30):
    """Mark old items as decayed."""
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible.")
        return

    count = store.decay_old_items(days)
    print(f"[evol-memory] Decayed {count} items (threshold: {days} days)")


def edms_tier_stats(project="."):
    """Show tier statistics."""
    store = _get_store()
    if not store:
        print("[evol-memory] EDMS no disponible.")
        return

    stats = store.get_tier_stats(project)
    print("=== Tier Stats ===")
    for tier, count in stats.items():
        print(f"  {tier}: {count}")
    print("==================")


def main():
    parser = argparse.ArgumentParser(description="Evol-DD Memory Engine")
    # Arg global --project ANTES del subcomando
    parser.add_argument("--project", default=".", help="Directorio del proyecto (default: $PWD)")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("load", help="Load session context (SessionStart)")
    sub.add_parser("stats", help="Show memory stats")

    p = sub.add_parser("summarize", help="Persist session to journal (Stop)")
    p.add_argument("--messages", help="JSONL messages file")

    p = sub.add_parser("compact", help="Compact long history")
    p.add_argument("--messages", help="JSONL messages file")

    p = sub.add_parser("search", help="Search memory")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=5)

    p = sub.add_parser("gc", help="Garbage collect expired tool results")
    p.add_argument("--days", type=int, default=TOOL_TTL_DAYS)

    p = sub.add_parser("sprint-close", help="Cierra sprint: crea acuerdos/memoria/sprint-NN.md + lecciones")
    p.add_argument("--sprint", required=True, help="Numero de sprint (1, '01', etc.)")
    p.add_argument("--memoria", default=None, help="Contenido para memoria/sprint-NN.md")
    p.add_argument("--lecciones", default=None, help="Contenido para lecciones/sprint-NN.md")
    p.add_argument("--force", action="store_true", help="Sobreescribir si ya existe")

    sub.add_parser("memory-split", help="Migra MEMORY.md monolitico a 3 atomos")

    # EDMS subcommands
    sub.add_parser("edms-stats", help="Show EDMS stats")

    p = sub.add_parser("edms-index", help="Index text into EDMS")
    p.add_argument("text", help="Text to index")
    p.add_argument("--tipo", default="artefacto", help="Tipo: decision|leccion|convencion|riesgo|artefacto|resumen|handoff")
    p.add_argument("--disciplinas", default=None, help="Comma-separated disciplinas")
    p.add_argument("--sprint", default=None, help="Sprint number")
    p.add_argument("--phase", default=None, help="Pipeline phase")
    p.add_argument("--agent", default=None, help="Agent name")
    p.add_argument("--importance", type=float, default=0.5, help="Importance 0-1")

    p = sub.add_parser("edms-search", help="Search EDMS")
    p.add_argument("query", help="Search query")
    p.add_argument("--tipo", default=None, help="Filter by tipo")
    p.add_argument("--disciplinas", default=None, help="Filter by disciplina")
    p.add_argument("--sprint", default=None, help="Filter by sprint")
    p.add_argument("--phase", default=None, help="Filter by phase")
    p.add_argument("--n", type=int, default=10, help="Max results")

    p = sub.add_parser("edms-wake-up", help="Generate wake-up context")
    p.add_argument("--sprint", default=None, help="Sprint number")

    p = sub.add_parser("edms-graph", help="Graph operations")
    graph_sub = p.add_subparsers(dest="graph_cmd")
    p_add = graph_sub.add_parser("add-node", help="Add node")
    p_add.add_argument("node_type", help="Node type (Proyecto, Sprint, etc.)")
    p_add.add_argument("props", help="JSON properties")
    p_add_rel = graph_sub.add_parser("add-relation", help="Add relation")
    p_add_rel.add_argument("source", help="Source node ID")
    p_add_rel.add_argument("relation", help="Relation type")
    p_add_rel.add_argument("target", help="Target node ID")
    p_trav = graph_sub.add_parser("traverse", help="Traverse graph")
    p_trav.add_argument("node_id", help="Starting node ID")
    p_trav.add_argument("--depth", type=int, default=2, help="Traversal depth")

    p = sub.add_parser("edms-bootstrap", help="Import acuerdos/ into EDMS")

    # 4-Tier consolidation commands
    p = sub.add_parser("edms-consolidate", help="Consolidate tiers (raw->compressed->memory->knowledge)")
    p.add_argument("from_tier", help="Source tier: raw|compressed|memory")
    p.add_argument("to_tier", help="Target tier: compressed|memory|knowledge")
    p.add_argument("--max", type=int, default=50, help="Max items to consolidate")

    p = sub.add_parser("edms-decay", help="Mark old items as decayed")
    p.add_argument("--days", type=int, default=30, help="Days threshold")

    sub.add_parser("edms-tier-stats", help="Show tier statistics")

    # FlowScript query commands
    p = sub.add_parser("edms-why", help="WHY: Find causes for a decision")
    p.add_argument("text", help="Decision text to investigate")

    sub.add_parser("edms-tensions", help="TENSIONS: Find conflicting lessons")
    sub.add_parser("edms-blocked", help="BLOCKED: Find blocking risks")

    p = sub.add_parser("edms-whatif", help="WHATIF: Simulate scenario")
    p.add_argument("scenario", help="Scenario to simulate")

    p = sub.add_parser("edms-alternatives", help="ALTERNATIVES: Find alternatives considered")
    p.add_argument("text", help="Decision text")

    # Team memory commands
    p = sub.add_parser("edms-agent-index", help="Index with agent namespace")
    p.add_argument("text", help="Text to index")
    p.add_argument("--agent", required=True, help="Agent ID")
    p.add_argument("--scope", default="shared", choices=["shared", "private"], help="Scope")

    p = sub.add_parser("edms-agent-context", help="Get agent-specific context")
    p.add_argument("--agent", required=True, help="Agent ID")

    args = parser.parse_args()

    if args.cmd == "load":
        load()
    elif args.cmd == "summarize":
        summarize(args.messages)
    elif args.cmd == "compact":
        compact(args.messages)
    elif args.cmd == "search":
        search(args.query, args.max)
    elif args.cmd == "gc":
        gc(args.days)
    elif args.cmd == "stats":
        stats()
    elif args.cmd == "sprint-close":
        sprint_close(
            sprint=args.sprint,
            project=args.project,
            memoria_content=args.memoria,
            lecciones_content=args.lecciones,
            force=args.force,
        )
        if args.json:
            import json as _json
            s = _sprint_num_str(args.sprint)
            print(_json.dumps({"ok": True, "sprint": s}))
    elif args.cmd == "memory-split":
        memory_split(project=args.project)
    elif args.cmd == "edms-index":
        edms_index(
            text=args.text, project=args.project, sprint=args.sprint,
            phase=args.phase, tipo=args.tipo, disciplinas=args.disciplinas,
            agent=args.agent, importance=args.importance,
        )
    elif args.cmd == "edms-search":
        edms_search(
            query=args.query, project=args.project, sprint=args.sprint,
            phase=args.phase, tipo=args.tipo, disciplinas=args.disciplinas,
            n_results=args.n,
        )
    elif args.cmd == "edms-wake-up":
        edms_wake_up(project=args.project, sprint=args.sprint)
    elif args.cmd == "edms-graph":
        if args.graph_cmd == "add-node":
            edms_graph_add_node(args.node_type, args.props)
        elif args.graph_cmd == "add-relation":
            edms_graph_add_relation(args.source, args.relation, args.target)
        elif args.graph_cmd == "traverse":
            edms_graph_traverse(args.node_id, args.depth)
        else:
            print("[evol-memory] Usage: edms-graph {add-node|add-relation|traverse}")
    elif args.cmd == "edms-bootstrap":
        edms_bootstrap(project=args.project)
    elif args.cmd == "edms-stats":
        edms_stats()
    elif args.cmd == "edms-consolidate":
        edms_consolidate(args.from_tier, args.to_tier, args.project, args.max)
    elif args.cmd == "edms-decay":
        edms_decay(args.project, args.days)
    elif args.cmd == "edms-tier-stats":
        edms_tier_stats(args.project)
    elif args.cmd == "edms-why":
        results = store.query_why(args.text) if store else []
        print(json.dumps(results, indent=2, ensure_ascii=False) if results else "No causes found")
    elif args.cmd == "edms-tensions":
        store = _get_store()
        results = store.query_tensions() if store else []
        print(json.dumps(results, indent=2, ensure_ascii=False) if results else "No tensions found")
    elif args.cmd == "edms-blocked":
        store = _get_store()
        results = store.query_blocked() if store else []
        print(json.dumps(results, indent=2, ensure_ascii=False) if results else "No blocking risks")
    elif args.cmd == "edms-whatif":
        store = _get_store()
        results = store.query_whatif(args.scenario) if store else []
        print(json.dumps(results, indent=2, ensure_ascii=False) if results else "No scenarios found")
    elif args.cmd == "edms-alternatives":
        store = _get_store()
        results = store.query_alternatives(args.text) if store else []
        print(json.dumps(results, indent=2, ensure_ascii=False) if results else "No alternatives found")
    elif args.cmd == "edms-agent-index":
        store = _get_store()
        if store:
            doc_id = store.index_agent(args.text, args.agent, args.scope)
            print(f"[evol-memory] Indexed for agent {args.agent}: {doc_id}")
        else:
            print("[evol-memory] EDMS no disponible.")
    elif args.cmd == "edms-agent-context":
        store = _get_store()
        if store:
            ctx = store.get_agent_context(args.agent, args.project)
            print(ctx)
        else:
            print("[evol-memory] EDMS no disponible.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()