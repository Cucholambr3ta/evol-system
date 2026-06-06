#!/usr/bin/env python3
"""Tests for evol-compliance.py — Compliance Auditor."""
import os, sys, json, tempfile, shutil, subprocess

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
PYTHON = sys.executable


def run_script(script, args, env=None, cwd=None):
    """Run a script via subprocess."""
    cmd = [PYTHON, os.path.join(SCRIPTS_DIR, script)] + args
    e = os.environ.copy()
    tmpdb = os.path.join(tempfile.mkdtemp(), "test-compliance.db")
    e["EVOL_STATE_DB"] = tmpdb
    if env:
        e.update(env)
    # Init DB first
    subprocess.run([PYTHON, os.path.join(SCRIPTS_DIR, "evol-state.py"), "init"],
                   capture_output=True, env=e)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or SCRIPTS_DIR, env=e)
    return result


def test_state_init():
    """State DB initializes with new tables."""
    tmpdb = os.path.join(tempfile.mkdtemp(), "test.db")
    result = run_script("evol-state.py", ["init"], env={"EVOL_STATE_DB": tmpdb})
    assert result.returncode == 0, f"init failed: {result.stderr}"
    assert "OK" in result.stdout

    import sqlite3
    conn = sqlite3.connect(tmpdb)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in c.fetchall()}
    conn.close()

    assert "phase_compliance" in tables, f"Missing phase_compliance. Found: {tables}"
    assert "violation_log" in tables, f"Missing violation_log. Found: {tables}"
    assert "lesson_tracking" in tables, f"Missing lesson_tracking. Found: {tables}"
    print("[OK] test_state_init")


def test_compliance_check_pass():
    """Compliance check returns PASS when artifacts exist."""
    tmpdir = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmpdir, "acuerdos", "idea"))
    with open(os.path.join(tmpdir, "acuerdos", "idea", "INDEX.md"), "w") as f:
        f.write("test")

    result = run_script("evol-compliance.py", ["check", "--fase", "0.5", "--json"], cwd=tmpdir)
    shutil.rmtree(tmpdir)

    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["verdict"] == "PASS", f"Expected PASS, got: {data['verdict']}"
    print("[OK] test_compliance_check_pass")


def test_compliance_check_block_missing():
    """Compliance check BLOCKS when artifacts are missing."""
    tmpdir = tempfile.mkdtemp()

    result = run_script("evol-compliance.py", ["check", "--fase", "0.5", "--json"], cwd=tmpdir)
    shutil.rmtree(tmpdir)

    assert result.returncode == 2, f"Expected exit 2 (BLOCK), got: {result.returncode}"
    data = json.loads(result.stdout)
    assert data["verdict"] == "BLOCK", f"Expected BLOCK, got: {data['verdict']}"
    assert "Missing" in data.get("block_reason", "") or "missing" in data.get("block_reason", "").lower()
    print("[OK] test_compliance_check_block_missing")


def test_compliance_record():
    """Compliance record updates entry."""
    tmpdir = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmpdir, "acuerdos", "idea"))
    with open(os.path.join(tmpdir, "acuerdos", "idea", "INDEX.md"), "w") as f:
        f.write("test")

    result = run_script("evol-compliance.py", [
        "record", "--fase", "0.5", "--agent", "test-agent", "--duration", "120.5", "--json"
    ], cwd=tmpdir)
    shutil.rmtree(tmpdir)

    assert result.returncode == 0, f"record failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["recorded"] is True
    print("[OK] test_compliance_record")


def test_check_lessons_empty():
    """check-lessons returns 0 when no lessons exist."""
    result = run_script("evol-compliance.py", ["check-lessons", "--fase", "0.5", "--json"])

    data = json.loads(result.stdout)
    assert data["pendientes_total"] == 0, f"Expected 0, got: {data['pendientes_total']}"
    print("[OK] test_check_lessons_empty")


def test_compliance_report():
    """Compliance report generates without errors."""
    tmpdir = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmpdir, "acuerdos", "auditoria"))

    result = run_script("evol-compliance.py", ["report", "--sprint", "1", "--json"], cwd=tmpdir)
    shutil.rmtree(tmpdir)

    assert result.returncode == 0, f"report failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["sprint"] == 1
    assert "summary" in data
    assert "compliance_score" in data["summary"]
    print("[OK] test_compliance_report")


def test_hooks_json_structure():
    """hooks.json has correct structure with new hooks."""
    hooks_path = os.path.join(SCRIPTS_DIR, "..", ".agent", "hooks", "hooks.json")
    with open(hooks_path) as f:
        data = json.load(f)

    standard_ids = {h["id"] for h in data["profiles"]["standard"]}
    strict_ids = {h["id"] for h in data["profiles"]["strict"]}

    assert "pre:phase:compliance-check" in standard_ids
    assert "pre:phase:lessons-check" in standard_ids
    assert "post:phase:gate-verify" in standard_ids
    assert "post:phase:record-metrics" in standard_ids
    assert "pre:commit:gitflow" in standard_ids
    assert "session:end:compliance-report" in strict_ids

    total = sum(len(v) for v in data["profiles"].values())
    assert total >= 19, f"Expected >=19 hooks total, got: {total}"
    print("[OK] test_hooks_json_structure")


def test_registry_has_18_agents():
    """registry.json has 18 core agents."""
    registry_path = os.path.join(SCRIPTS_DIR, "..", "prompts", "agents", "registry.json")
    with open(registry_path) as f:
        data = json.load(f)

    core = [a for a in data["agents"] if a["category"] == "core"]
    names = {a["name"] for a in core}

    assert len(core) == 18, f"Expected 18 core agents, got: {len(core)}"
    assert "evol-compliance-auditor" in names
    print("[OK] test_registry_has_18_agents")


def test_agent_md_exists():
    """Agent definition file exists."""
    path = os.path.join(SCRIPTS_DIR, "..", "prompts", "agents", "core", "evol-compliance-auditor.md")
    assert os.path.exists(path), f"Missing: {path}"
    content = open(path).read()
    assert "evol-compliance-auditor" in content
    print("[OK] test_agent_md_exists")


def test_workflow_md_exists():
    """Workflow file exists."""
    path = os.path.join(SCRIPTS_DIR, "..", ".agent", "workflows", "evol-compliance-auditor.md")
    assert os.path.exists(path), f"Missing: {path}"
    content = open(path).read()
    assert "compliance-audit" in content
    print("[OK] test_workflow_md_exists")


if __name__ == "__main__":
    test_state_init()
    test_compliance_check_pass()
    test_compliance_check_block_missing()
    test_compliance_record()
    test_check_lessons_empty()
    test_compliance_report()
    test_hooks_json_structure()
    test_registry_has_18_agents()
    test_agent_md_exists()
    test_workflow_md_exists()
    print("\n=== ALL 10 TESTS PASSED ===")
