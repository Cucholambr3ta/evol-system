import pytest

def test_state_init():
    import subprocess
    result = subprocess.run(["python3", "scripts/evol-state.py", "init"], capture_output=True)
    assert result.returncode == 0

def test_gate_init():
    import subprocess
    result = subprocess.run(["python3", "scripts/evol-gate.py", "init"], capture_output=True)
    assert result.returncode == 0