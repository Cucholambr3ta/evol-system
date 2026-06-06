#!/usr/bin/env python3
"""Tests for evol-memory.py — Memory Engine."""
import os, sys, json, tempfile, shutil, subprocess

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
PYTHON = sys.executable


def run_script(script, args, cwd=None):
    cmd = [PYTHON, os.path.join(SCRIPTS_DIR, script)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or SCRIPTS_DIR)
    return result


def test_sprint_close_creates_files():
    """sprint-close creates memory and lessons files."""
    tmpdir = tempfile.mkdtemp()
    acuerdos = os.path.join(tmpdir, "acuerdos")
    os.makedirs(os.path.join(acuerdos, "memoria"))
    os.makedirs(os.path.join(acuerdos, "lecciones"))

    result = run_script("evol-memory.py", [
        "--project", tmpdir, "sprint-close", "--sprint", "99",
        "--memoria", "# Sprint 99 Memory\n\n## Hitos\n\n- Test",
        "--lecciones", "# Sprint 99 Lessons\n\n### [TESTING] Test lesson\n\n**Contexto:** Test\n**Problema:** Test\n**Causa raiz:** Test\n**Leccion:** Test\n**Aplica a:** Test",
    ], cwd=tmpdir)

    assert os.path.exists(os.path.join(acuerdos, "memoria", "sprint-99.md"))
    assert os.path.exists(os.path.join(acuerdos, "lecciones", "sprint-99.md"))

    mem_content = open(os.path.join(acuerdos, "memoria", "sprint-99.md")).read()
    assert "Sprint 99" in mem_content
    assert "Hitos" in mem_content

    les_content = open(os.path.join(acuerdos, "lecciones", "sprint-99.md")).read()
    assert "TESTING" in les_content
    print("[OK] test_sprint_close_creates_files")


def test_sprint_close_idempotent():
    """sprint-close doesn't overwrite existing files without --force."""
    tmpdir = tempfile.mkdtemp()
    acuerdos = os.path.join(tmpdir, "acuerdos")
    os.makedirs(os.path.join(acuerdos, "memoria"))
    os.makedirs(os.path.join(acuerdos, "lecciones"))

    # Create existing file
    with open(os.path.join(acuerdos, "memoria", "sprint-98.md"), "w") as f:
        f.write("# Original content")

    result = run_script("evol-memory.py", [
        "--project", tmpdir, "sprint-close", "--sprint", "98",
        "--memoria", "# New content",
    ], cwd=tmpdir)

    content = open(os.path.join(acuerdos, "memoria", "sprint-98.md")).read()
    assert "Original content" in content, "File should not be overwritten without --force"
    print("[OK] test_sprint_close_idempotent")


def test_memory_atoms_created():
    """sprint-close creates memory atoms if missing."""
    tmpdir = tempfile.mkdtemp()
    acuerdos = os.path.join(tmpdir, "acuerdos")
    mem_dir = os.path.join(acuerdos, "memoria")
    os.makedirs(mem_dir)
    os.makedirs(os.path.join(acuerdos, "lecciones"))

    result = run_script("evol-memory.py", [
        "--project", tmpdir, "sprint-close", "--sprint", "97",
    ], cwd=tmpdir)

    assert os.path.exists(os.path.join(mem_dir, "decisiones.md"))
    assert os.path.exists(os.path.join(mem_dir, "convenciones.md"))
    assert os.path.exists(os.path.join(mem_dir, "riesgos.md"))
    assert os.path.exists(os.path.join(mem_dir, "MEMORY.md"))
    print("[OK] test_memory_atoms_created")


def test_memory_aggregate_regenerated():
    """MEMORY.md is regenerated from atoms."""
    tmpdir = tempfile.mkdtemp()
    mem_dir = os.path.join(tmpdir, "acuerdos", "memoria")
    os.makedirs(mem_dir)
    os.makedirs(os.path.join(tmpdir, "acuerdos", "lecciones"))

    # Create atoms
    with open(os.path.join(mem_dir, "decisiones.md"), "w") as f:
        f.write("# Decisiones\n\n- Decision 1\n")
    with open(os.path.join(mem_dir, "convenciones.md"), "w") as f:
        f.write("# Convenciones\n\n- Convencion 1\n")
    with open(os.path.join(mem_dir, "riesgos.md"), "w") as f:
        f.write("# Riesgos\n\n- Riesgo 1\n")

    # Create old MEMORY.md
    with open(os.path.join(mem_dir, "MEMORY.md"), "w") as f:
        f.write("# Old aggregate\n")

    result = run_script("evol-memory.py", [
        "--project", tmpdir, "sprint-close", "--sprint", "96",
    ], cwd=tmpdir)

    content = open(os.path.join(mem_dir, "MEMORY.md")).read()
    assert "Decision 1" in content
    assert "Convencion 1" in content
    assert "Riesgo 1" in content
    assert "Old aggregate" not in content
    print("[OK] test_memory_aggregate_regenerated")


def test_lecciones_index_updated():
    """sprint-close updates the lessons INDEX.md."""
    tmpdir = tempfile.mkdtemp()
    acuerdos = os.path.join(tmpdir, "acuerdos")
    os.makedirs(os.path.join(acuerdos, "memoria"))
    les_dir = os.path.join(acuerdos, "lecciones")
    os.makedirs(les_dir)

    # Create existing index
    with open(os.path.join(les_dir, "INDEX.md"), "w") as f:
        f.write("# Lecciones Index\n\n| Sprint | Archivo | Fecha |\n|--------|---------|-------|\n")

    result = run_script("evol-memory.py", [
        "--project", tmpdir, "sprint-close", "--sprint", "95",
    ], cwd=tmpdir)

    content = open(os.path.join(les_dir, "INDEX.md")).read()
    assert "sprint-95" in content
    print("[OK] test_lecciones_index_updated")


if __name__ == "__main__":
    test_sprint_close_creates_files()
    test_sprint_close_idempotent()
    test_memory_atoms_created()
    test_memory_aggregate_regenerated()
    test_lecciones_index_updated()
    print("\n=== ALL 5 MEMORY TESTS PASSED ===")
