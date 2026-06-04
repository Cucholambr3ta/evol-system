"""Tests del enforcement FSM en evol-gate.py (Incremento 2, heredado de X-DD).

Cadena de fases + separacion autor!=aprobador + overrides.
"""
import os
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "evol-gate.py"


def _run(args, cwd, env_extra=None):
    env = os.environ.copy()
    env["EVOL_DATA_DIR"] = str(cwd)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        cwd=str(cwd), env=env, capture_output=True, text=True,
    )


@pytest.fixture
def project(tmp_path):
    _run(["init"], tmp_path)
    return tmp_path


# ── cadena de fases ───────────────────────────────────────────────────────────

def test_plan_blocked_without_chain(project):
    r = _run(["approve", "--phase", "plan", "--approver", "bob"], project)
    assert r.returncode == 1
    assert "fases previas sin aprobar" in r.stderr


def test_briefing_first_phase_passes(project):
    r = _run(["approve", "--phase", "briefing", "--approver", "alice"], project)
    assert r.returncode == 0


def test_full_chain_in_order(project):
    assert _run(["approve", "--phase", "briefing", "--approver", "a"], project).returncode == 0
    assert _run(["approve", "--phase", "spec", "--approver", "b"], project).returncode == 0
    # plan requiere grill; sin PLAN.md el grill no aplica, cadena OK
    assert _run(["approve", "--phase", "plan", "--approver", "c"], project).returncode == 0


def test_skip_chain_override(project):
    r = _run(["approve", "--phase", "qa", "--approver", "bob"],
             project, {"EVOL_SKIP_CHAIN": "1"})
    assert r.returncode == 0
    assert "EVOL_SKIP_CHAIN=1" in r.stderr


def test_free_phase_not_chained(project):
    # fase fuera de PHASE_ORDER no se encadena
    r = _run(["approve", "--phase", "custom-phase", "--approver", "bob"], project)
    assert r.returncode == 0


# ── separacion autor != aprobador ─────────────────────────────────────────────

def test_segregation_blocks_self_approval(project):
    _run(["approve", "--phase", "briefing", "--approver", "alice"], project)
    _run(["set-author", "--phase", "spec", "--author", "alice"], project)
    r = _run(["approve", "--phase", "spec", "--approver", "alice"], project)
    assert r.returncode == 1
    assert "no puede ser el autor" in r.stderr


def test_segregation_allows_different_approver(project):
    _run(["approve", "--phase", "briefing", "--approver", "alice"], project)
    _run(["set-author", "--phase", "spec", "--author", "alice"], project)
    r = _run(["approve", "--phase", "spec", "--approver", "bob"], project)
    assert r.returncode == 0


def test_segregation_override(project):
    _run(["approve", "--phase", "briefing", "--approver", "alice"], project)
    _run(["set-author", "--phase", "spec", "--author", "alice"], project)
    r = _run(["approve", "--phase", "spec", "--approver", "alice"],
             project, {"EVOL_SKIP_SEGREGATION": "1"})
    assert r.returncode == 0


def test_set_author_writes_marker(project):
    _run(["set-author", "--phase", "spec", "--author", "dave"], project)
    marker = project / ".evol" / ".author-spec"
    assert marker.exists()
    assert marker.read_text().strip() == "dave"
