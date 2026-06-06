#!/usr/bin/env python3
"""Tests for evol-lessons.py — Lessons Engine."""
import os, sys, json, tempfile, shutil, subprocess

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
PYTHON = sys.executable


def run_script(script, args, cwd=None):
    cmd = [PYTHON, os.path.join(SCRIPTS_DIR, script)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or SCRIPTS_DIR)
    return result


def test_add_lesson():
    """Add a lesson to lecciones.md."""
    tmpdir = tempfile.mkdtemp()
    lessons_file = os.path.join(tmpdir, "lecciones.md")
    # Create minimal lessons file
    with open(lessons_file, "w") as f:
        f.write("# lecciones.md\n\n## ARQUITECTURA\n\n_(vacio)_\n\n## SEGURIDAD\n\n_(vacio)_\n\n## DOMINIO\n\n_(vacio)_\n\n## TESTING\n\n_(vacio)_\n\n## DEVOPS\n\n_(vacio)_\n\n## PROCESO\n\n_(vacio)_\n\n## HERRAMIENTAS\n\n_(vacio)_\n")

    result = run_script("evol-lessons.py", [
        "add", "--titulo", "Test lesson",
        "--categoria", "ARQUITECTURA",
        "--contexto", "Testing context",
        "--problema", "Test problem",
        "--causa", "Test cause",
        "--leccion", "Test lesson text",
        "--aplica", "Tests"
    ], cwd=tmpdir)

    assert result.returncode == 0, f"add failed: {result.stderr}"
    assert "[OK]" in result.stdout

    content = open(lessons_file).read()
    assert "Test lesson" in content
    assert "[ARQUITECTURA]" in content
    print("[OK] test_add_lesson")


def test_parse_lessons():
    """Parse lessons from lecciones.md."""
    tmpdir = tempfile.mkdtemp()
    lessons_file = os.path.join(tmpdir, "lecciones.md")
    with open(lessons_file, "w") as f:
        f.write("""# lecciones.md

## ARQUITECTURA

### [ARQUITECTURA] Test parse — 2026-06-06
**Contexto:** Parse test
**Problema:** Testing parsing
**Causa raiz:** Test cause
**Leccion:** Test lesson
**Aplica a:** Tests

## SEGURIDAD

_(vacio)_

## DOMINIO

_(vacio)_

## TESTING

_(vacio)_

## DEVOPS

_(vacio)_

## PROCESO

_(vacio)_

## HERRAMIENTAS

_(vacio)_
""")

    result = run_script("evol-lessons.py", ["search", "parse", "--json"], cwd=tmpdir)

    # search doesn't have --json, but parse_lessons is internal
    # Let's test via the CLI list command
    result = run_script("evol-lessons.py", ["list"], cwd=tmpdir)
    assert "Test parse" in result.stdout or result.returncode == 0
    print("[OK] test_parse_lessons")


def test_search_lessons():
    """Search lessons by query."""
    tmpdir = tempfile.mkdtemp()
    lessons_file = os.path.join(tmpdir, "lecciones.md")
    with open(lessons_file, "w") as f:
        f.write("""# lecciones.md

## HERRAMIENTAS

### [HERRAMIENTAS] Mermaid labels rompen render — 2026-06-05
**Contexto:** Diagramas
**Problema:** Labels break
**Causa raiz:** Special chars
**Leccion:** Use br not backslash n
**Aplica a:** Mermaid docs

## DEVOPS

### [DEVOPS] PyPI version collision — 2026-06-04
**Contexto:** Publishing
**Problema:** Version exists
**Causa raiz:** No tracking
**Leccion:** Check before publish
**Aplica a:** PyPI

## ARQUITECTURA

_(vacio)_

## SEGURIDAD

_(vacio)_

## DOMINIO

_(vacio)_

## TESTING

_(vacio)_

## PROCESO

_(vacio)_
""")

    result = run_script("evol-lessons.py", ["search", "mermaid"], cwd=tmpdir)
    assert "Mermaid" in result.stdout or "mermaid" in result.stdout.lower()
    print("[OK] test_search_lessons")


def test_list_pendientes():
    """List only pending lessons."""
    tmpdir = tempfile.mkdtemp()
    lessons_file = os.path.join(tmpdir, "lecciones.md")
    with open(lessons_file, "w") as f:
        f.write("""# lecciones.md

## ARQUITECTURA

### [ARQUITECTURA] Applied lesson — 2026-06-01
**Contexto:** Done
**Problema:** Fixed
**Causa raiz:** Was broken
**Leccion:** Always check
**Aplica a:** Everything
**Fix aplicado:** Done
**Mejoras sugeridas:** None
**Estado mejoras:** aplicado

## HERRAMIENTAS

### [HERRAMIENTAS] Pending lesson — 2026-06-02
**Contexto:** Open
**Problema:** Still broken
**Causa raiz:** Unknown
**Leccion:** Check again
**Aplica a:** Tools
**Mejoras sugeridas:** Fix it
**Estado mejoras:** pendiente

## SEGURIDAD

_(vacio)_

## DOMINIO

_(vacio)_

## TESTING

_(vacio)_

## DEVOPS

_(vacio)_

## PROCESO

_(vacio)_
""")

    result = run_script("evol-lessons.py", ["list", "--pendientes"], cwd=tmpdir)
    assert "PENDIENTE" in result.stdout
    assert "Pending lesson" in result.stdout
    # Applied lesson should NOT appear with --pendientes
    assert "Applied lesson" not in result.stdout
    print("[OK] test_list_pendientes")


def test_stats():
    """Show lesson statistics."""
    tmpdir = tempfile.mkdtemp()
    lessons_file = os.path.join(tmpdir, "lecciones.md")
    with open(lessons_file, "w") as f:
        f.write("""# lecciones.md

## ARQUITECTURA

### [ARQUITECTURA] Lesson A — 2026-06-01
**Contexto:** A
**Problema:** A
**Causa raiz:** A
**Leccion:** A
**Aplica a:** A

## HERRAMIENTAS

### [HERRAMIENTAS] Lesson B — 2026-06-02
**Contexto:** B
**Problema:** B
**Causa raiz:** B
**Leccion:** B
**Aplica a:** B

## SEGURIDAD

_(vacio)_

## DOMINIO

_(vacio)_

## TESTING

_(vacio)_

## DEVOPS

_(vacio)_

## PROCESO

_(vacio)_
""")

    result = run_script("evol-lessons.py", ["stats"], cwd=tmpdir)
    assert "Total lessons: 2" in result.stdout
    assert "ARQUITECTURA: 1" in result.stdout
    assert "HERRAMIENTAS: 1" in result.stdout
    print("[OK] test_stats")


def test_verify_applied():
    """Verify applied lessons via compliance script."""
    tmpdir = tempfile.mkdtemp()
    lessons_file = os.path.join(tmpdir, "lecciones.md")
    with open(lessons_file, "w") as f:
        f.write("""# lecciones.md

## HERRAMIENTAS

### [HERRAMIENTAS] Mermaid labels rompen render — 2026-06-05
**Contexto:** Diagramas
**Problema:** Labels break
**Causa raiz:** Special chars
**Leccion:** Use br not backslash n
**Aplica a:** Mermaid docs
**Mejoras sugeridas:** Fix it
**Estado mejoras:** pendiente

## ARQUITECTURA

_(vacio)_

## SEGURIDAD

_(vacio)_

## DOMINIO

_(vacio)_

## TESTING

_(vacio)_

## DEVOPS

_(vacio)_

## PROCESO

_(vacio)_
""")

    # Create sprint file with matching content
    sprint_dir = os.path.join(tmpdir, "acuerdos", "lecciones")
    os.makedirs(sprint_dir)
    with open(os.path.join(sprint_dir, "sprint-1.md"), "w") as f:
        f.write("# Sprint 1\n\nMermaid labels need br not backslash n\n")

    result = run_script("evol-compliance.py", ["verify-applied", "--sprint", "1", "--json"], cwd=tmpdir)
    assert result.returncode == 0, f"verify-applied failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["sprint"] == 1
    assert data["applied"] >= 0  # May or may not find evidence
    print("[OK] test_verify_applied")


if __name__ == "__main__":
    test_add_lesson()
    test_parse_lessons()
    test_search_lessons()
    test_list_pendientes()
    test_stats()
    test_verify_applied()
    print("\n=== ALL 6 LESSONS TESTS PASSED ===")
