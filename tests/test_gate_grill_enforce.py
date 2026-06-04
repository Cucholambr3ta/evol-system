"""Tests del enforcement grill-me en el gate del plan (evol-gate.py)."""
import hashlib, importlib.util, os, subprocess, sys
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
        cwd=str(cwd), env=env, capture_output=True, text=True
    )


@pytest.fixture
def project(tmp_path):
    _run(["init"], tmp_path)
    return tmp_path


def test_plan_blocked_without_grill(project):
    (project / "PLAN.md").write_text("# Plan\n")
    r = _run(["approve", "--phase", "plan"], project)
    assert r.returncode == 1
    assert "BLOQUEADO" in r.stderr


def test_plan_passes_after_grill_done(project):
    (project / "PLAN.md").write_text("# Plan\n")
    _run(["grill-done"], project)
    r = _run(["approve", "--phase", "plan"], project)
    assert r.returncode == 0
    assert "APROBADO" in r.stdout


def test_plan_blocked_after_edit(project):
    (project / "PLAN.md").write_text("# Plan\n")
    _run(["grill-done"], project)
    (project / "PLAN.md").write_text("# Plan editado\n")
    r = _run(["approve", "--phase", "plan"], project)
    assert r.returncode == 1
    assert "cambio despues" in r.stderr


def test_override_skip_grill(project):
    (project / "PLAN.md").write_text("# Plan\n")
    r = _run(["approve", "--phase", "plan"], project, {"EVOL_SKIP_GRILL": "1"})
    assert r.returncode == 0


def test_non_plan_phase_unaffected(project):
    r = _run(["approve", "--phase", "spec"], project)
    assert r.returncode == 0


def test_grill_done_records_sha(project):
    (project / "PLAN.md").write_text("# Plan\n")
    _run(["grill-done"], project)
    marker = project / ".evol" / ".grill-done-plan"
    assert marker.exists()
    expected = hashlib.sha256((project / "PLAN.md").read_bytes()).hexdigest()
    assert marker.read_text().strip() == expected


def test_transition_to_plan_enforced(project):
    (project / "PLAN.md").write_text("# Plan\n")
    r = _run(["transition", "--from", "spec", "--to", "plan"], project)
    assert r.returncode == 1
    assert "BLOQUEADO" in r.stderr
