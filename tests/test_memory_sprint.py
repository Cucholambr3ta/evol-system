"""Tests para evol-memory.py sprint-close — INC E5."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "evol_memory",
    Path(__file__).parent.parent / "scripts" / "evol-memory.py",
)
evol_memory = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(evol_memory)


def run_sprint_close(tmp_path, sprint, **kwargs):
    return evol_memory.sprint_close(
        sprint=sprint,
        project=str(tmp_path),
        memoria_content=kwargs.get("memoria_content"),
        lecciones_content=kwargs.get("lecciones_content"),
        force=kwargs.get("force", False),
    )


def test_sprint_close_crea_memoria_file(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    assert (tmp_path / "acuerdos" / "memoria" / "sprint-01.md").exists()


def test_sprint_close_crea_lecciones_file(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    assert (tmp_path / "acuerdos" / "lecciones" / "sprint-01.md").exists()


def test_sprint_close_crea_index(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    idx = tmp_path / "acuerdos" / "lecciones" / "INDEX.md"
    assert idx.exists()
    assert "sprint-01" in idx.read_text()


def test_sprint_close_crea_memory_md(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    mem = tmp_path / "acuerdos" / "memoria" / "MEMORY.md"
    assert mem.exists()
    assert "Hechos persistentes" in mem.read_text()


def test_sprint_close_numero_normalizado(tmp_path):
    run_sprint_close(tmp_path, sprint="3")
    assert (tmp_path / "acuerdos" / "memoria" / "sprint-03.md").exists()
    run_sprint_close(tmp_path, sprint=12)
    assert (tmp_path / "acuerdos" / "memoria" / "sprint-12.md").exists()


def test_sprint_close_no_sobreescribe_sin_force(tmp_path):
    run_sprint_close(tmp_path, sprint=1, memoria_content="# Original\n")
    run_sprint_close(tmp_path, sprint=1, memoria_content="# Nuevo\n")
    content = (tmp_path / "acuerdos" / "memoria" / "sprint-01.md").read_text()
    assert "Original" in content
    assert "Nuevo" not in content


def test_sprint_close_force_sobreescribe(tmp_path):
    run_sprint_close(tmp_path, sprint=1, memoria_content="# Original\n")
    run_sprint_close(tmp_path, sprint=1, memoria_content="# Nuevo\n", force=True)
    content = (tmp_path / "acuerdos" / "memoria" / "sprint-01.md").read_text()
    assert "Nuevo" in content


def test_sprint_close_contenido_personalizado(tmp_path):
    mem = "# Sprint 5\n\n## Hitos\n- auth implementado\n"
    les = "### [ARQUITECTURA] Patron X\n**Contexto:** ...\n"
    run_sprint_close(tmp_path, sprint=5, memoria_content=mem, lecciones_content=les)
    assert (tmp_path / "acuerdos" / "memoria" / "sprint-05.md").read_text() == mem
    assert (tmp_path / "acuerdos" / "lecciones" / "sprint-05.md").read_text() == les


def test_sprint_close_index_acumula_multiples_sprints(tmp_path):
    for n in [1, 2, 3]:
        run_sprint_close(tmp_path, sprint=n)
    idx = (tmp_path / "acuerdos" / "lecciones" / "INDEX.md").read_text()
    assert "sprint-01" in idx
    assert "sprint-02" in idx
    assert "sprint-03" in idx


def test_sprint_close_index_no_duplica_entrada(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    run_sprint_close(tmp_path, sprint=1, force=True)
    idx = (tmp_path / "acuerdos" / "lecciones" / "INDEX.md").read_text()
    rows = [l for l in idx.splitlines() if l.startswith("| sprint-01 |")]
    assert len(rows) == 1


def test_sprint_close_arg_project_funciona(tmp_path):
    """El arg --project debe pasarse ANTES del subcomando en CLI (argparse global)."""
    evol_memory.sprint_close(sprint=2, project=str(tmp_path))
    assert (tmp_path / "acuerdos" / "memoria" / "sprint-02.md").exists()


# ── MEMORY.md atomico (herencia atomicidad) ───────────────────────────────────

def test_sprint_close_crea_3_atomos(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    mem = tmp_path / "acuerdos" / "memoria"
    assert (mem / "decisiones.md").exists()
    assert (mem / "convenciones.md").exists()
    assert (mem / "riesgos.md").exists()


def test_memory_aggregate_banner(tmp_path):
    run_sprint_close(tmp_path, sprint=1)
    content = (tmp_path / "acuerdos" / "memoria" / "MEMORY.md").read_text()
    assert "GENERADO automaticamente" in content


def test_memory_split_migra_legacy(tmp_path):
    mem = tmp_path / "acuerdos" / "memoria"
    mem.mkdir(parents=True)
    (mem / "MEMORY.md").write_text(
        "# MEMORY.md\n\n## Decisiones clave\n- Usar Redis.\n\n"
        "## Convenciones\n- TDD.\n\n## Riesgos activos\n- Lock-in.\n"
    )
    evol_memory.memory_split(project=str(tmp_path))
    assert "Usar Redis" in (mem / "decisiones.md").read_text()
    assert "GENERADO automaticamente" in (mem / "MEMORY.md").read_text()
