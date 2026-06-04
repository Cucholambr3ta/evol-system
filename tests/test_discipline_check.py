"""Tests evol-discipline-check.py — INC E8. 2 tests/disciplina: positivo + negativo."""
import os, sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import importlib.util
_s = importlib.util.spec_from_file_location(
    "evol_dc", Path(__file__).parent.parent / "scripts" / "evol-discipline-check.py"
)
evol_dc = importlib.util.module_from_spec(_s); _s.loader.exec_module(evol_dc)


def make(tmp, rel, content):
    p = tmp / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content); return tmp


# ── SDD ───────────────────────────────────────────────────────────────────────

def test_sdd_pasa(tmp_path):
    make(tmp_path, ".evol/briefing/SPEC.md", """# SPEC
## Objetivo
Resolver gestion de proyectos distribuidos.
## Alcance
Modulo de usuarios y tareas del equipo.
## Criterios de aceptacion
- Usuario puede crear proyecto
## NFR
- Disponibilidad 99.9%
""")
    assert evol_dc.check_sdd(tmp_path) == []


def test_sdd_falla_sin_criterios(tmp_path):
    make(tmp_path, ".evol/briefing/SPEC.md", """# SPEC
## Objetivo
Sistema de gestion de tareas para equipos distribuidos.
## Alcance
Incluye modulo de usuarios, proyectos y reportes de actividad.
## Arquitectura
Monolito con separacion de capas.
""")
    errors = evol_dc.check_sdd(tmp_path)
    assert errors
    assert any("aceptacion" in e.lower() or "criterio" in e.lower() or "nfr" in e.lower() for e in errors)


# ── FDD ───────────────────────────────────────────────────────────────────────

def test_fdd_pasa(tmp_path):
    make(tmp_path, ".evol/briefing/FEATURES.md", """# FEATURES
## F-01: Autenticacion
**Prioridad:** Must Have
**Criterios:** Login con email y password.
""")
    assert evol_dc.check_fdd(tmp_path) == []


def test_fdd_falla_sin_priorizacion(tmp_path):
    make(tmp_path, ".evol/briefing/FEATURES.md", """# FEATURES
## F-01: Autenticacion
Implementar login.
## F-02: Dashboard
Ver proyectos.
""")
    errors = evol_dc.check_fdd(tmp_path)
    assert any("prioriza" in e.lower() for e in errors)


# ── DDD ───────────────────────────────────────────────────────────────────────

def test_ddd_pasa(tmp_path):
    make(tmp_path, ".evol/spec/DOMAIN.md", """# DOMAIN
## Ubiquitous Language
- **Proyecto:** Unidad de trabajo agrupada por objetivo.
## Bounded Contexts
### Gestion de Proyectos
Responsable de proyectos.
## Aggregates
- Proyecto (root)
""")
    assert evol_dc.check_ddd(tmp_path) == []


def test_ddd_falla_sin_ubiquitous(tmp_path):
    make(tmp_path, ".evol/spec/DOMAIN.md", """# DOMAIN
## Arquitectura
Monolito con modulos separados.
## Bounded Contexts
### Gestion de Proyectos
Responsable de crear proyectos del equipo.
## Aggregates
- Proyecto (root), Tarea (root)
""")
    errors = evol_dc.check_ddd(tmp_path)
    assert errors
    assert any("ubiquitous" in e.lower() or "glosario" in e.lower() for e in errors)


# ── Threat-Driven ─────────────────────────────────────────────────────────────

def test_threat_driven_pasa(tmp_path):
    make(tmp_path, ".evol/spec/THREATS.md", """# THREATS
## STRIDE
### Spoofing
Control propuesto: MFA obligatorio.
### Tampering
Control: validacion ownership middleware.
""")
    assert evol_dc.check_threat_driven(tmp_path) == []


def test_threat_driven_falla_sin_stride(tmp_path):
    make(tmp_path, ".evol/spec/THREATS.md", """# THREATS
## Riesgos generales
- El sistema puede ser hackeado.
- Posibles problemas de performance.
""")
    errors = evol_dc.check_threat_driven(tmp_path)
    assert any("stride" in e.lower() for e in errors)


# ── BDD ───────────────────────────────────────────────────────────────────────

def test_bdd_pasa(tmp_path):
    make(tmp_path, "tests/features/login.feature", """Feature: Login
  Scenario: Happy path
    Given credenciales validas
    When hace login
    Then accede al dashboard

  Scenario: Error — credenciales invalidas
    Given password incorrecta
    When intenta login
    Then ve error

  Scenario: Borde — cuenta bloqueada
    Given 5 intentos fallidos
    When intenta nuevamente
    Then cuenta bloqueada
""")
    assert evol_dc.check_bdd(tmp_path) == []


def test_bdd_falla_solo_happy_path(tmp_path):
    make(tmp_path, "tests/features/login.feature", """Feature: Login
  Scenario: Login exitoso
    Given credenciales validas
    When hace login
    Then accede
""")
    errors = evol_dc.check_bdd(tmp_path)
    assert errors


def test_bdd_sin_features_ok(tmp_path):
    assert evol_dc.check_bdd(tmp_path) == []


# ── TDD ───────────────────────────────────────────────────────────────────────

def test_tdd_pasa(tmp_path):
    f = tmp_path / "tests" / "unit" / "test_auth.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("def test_login(): assert True")
    assert evol_dc.check_tdd(tmp_path) == []


def test_tdd_falla_sin_tests(tmp_path):
    assert evol_dc.check_tdd(tmp_path)


# ── STDD ──────────────────────────────────────────────────────────────────────

def test_stdd_pasa(tmp_path):
    make(tmp_path, ".evol/spec/THREATS.md", "# THREATS\n\n## STRIDE\n\n### Spoofing\nControl: rate limiting.\n")
    f = tmp_path / "tests" / "security" / "test_auth_security.py"
    f.parent.mkdir(parents=True, exist_ok=True); f.write_text("def test_rate(): pass")
    assert evol_dc.check_stdd(tmp_path) == []


def test_stdd_falla_sin_security_tests(tmp_path):
    make(tmp_path, ".evol/spec/THREATS.md", "# THREATS\n\n## STRIDE\n\n### Spoofing\nControl: auth fuerte.\n")
    errors = evol_dc.check_stdd(tmp_path)
    assert any("stdd" in e.lower() or "security" in e.lower() for e in errors)


# ── SecDD ─────────────────────────────────────────────────────────────────────

def test_secdd_pasa(tmp_path):
    make(tmp_path, ".evol/qa/QA_REPORT.md", """# QA Report
## SAST
Semgrep: 0 criticos.
## DAST
OWASP ZAP: 0 high.
## Secrets
Gitleaks: limpio.
""")
    assert evol_dc.check_secdd(tmp_path) == []


def test_secdd_falla_sin_dast(tmp_path):
    make(tmp_path, ".evol/qa/QA_REPORT.md", """# QA Report
## SAST
Bandit: 0 issues.
## Secrets
Gitleaks: limpio.
""")
    errors = evol_dc.check_secdd(tmp_path)
    assert any("dast" in e.lower() for e in errors)


# ── EVOL_SKIP_DISCIPLINE override ─────────────────────────────────────────────

def test_skip_discipline_omite_checks(tmp_path, monkeypatch):
    monkeypatch.setenv("EVOL_SKIP_DISCIPLINE", "1")
    make(tmp_path, ".evol/briefing/SPEC.md", "# vacio")
    assert evol_dc.check_phase(tmp_path, "briefing") == []


def test_discipline_activo_detecta_violations(tmp_path, monkeypatch):
    monkeypatch.delenv("EVOL_SKIP_DISCIPLINE", raising=False)
    make(tmp_path, ".evol/briefing/SPEC.md", "# vacio")
    assert evol_dc.check_phase(tmp_path, "briefing")


# ── check_phase dispatcher ────────────────────────────────────────────────────

def test_check_phase_briefing_corre_sdd_y_fdd(tmp_path):
    errors = evol_dc.check_phase(tmp_path, "briefing")
    assert any("SDD" in e or "SPEC" in e for e in errors)
    assert any("FDD" in e or "FEATURES" in e for e in errors)


def test_check_phase_retro_sin_checks(tmp_path):
    assert evol_dc.check_phase(tmp_path, "retro") == []
