"""Negative tests for gate HMAC chain integrity."""
import os, sys, json, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def run_gate(args, cwd=None, env=None):
    import subprocess
    if cwd is None:
        cwd = os.path.dirname(os.path.dirname(__file__))
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    result = subprocess.run(
        [sys.executable, "scripts/evol-gate.py"] + args,
        capture_output=True, text=True, cwd=cwd, env=full_env
    )
    return result

class TestGateHMACNegative:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp(prefix="test_gate_")
        self.env = {"EVOL_DATA_DIR": self.tmpdir}
        self.key_file = os.path.join(self.tmpdir, ".evol", ".gate-key")
        self.log_file = os.path.join(self.tmpdir, ".evol", ".gate-log.jsonl")

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_log_tampered(self):
        """Log tampering should be detected."""
        run_gate(["init"], env=self.env)
        run_gate(["approve", "--phase", "briefing"], env=self.env)
        with open(self.log_file) as f:
            entry = json.loads(f.readline())
        entry["payload"]["phase"] = "TAMPERED"
        with open(self.log_file, "w") as f:
            f.write(json.dumps(entry) + "\n")
        result = run_gate(["validate"], env=self.env)
        assert result.returncode != 0, f"validate should fail when log is tampered: {result.stdout}"

    def test_invalid_signature(self):
        """Invalid signature should be rejected."""
        run_gate(["init"], env=self.env)
        run_gate(["approve", "--phase", "briefing"], env=self.env)
        with open(self.log_file) as f:
            entry = json.loads(f.readline())
        entry["signature"] = "INVALID_SIGNATURE_AAAA"
        with open(self.log_file, "w") as f:
            f.write(json.dumps(entry) + "\n")
        result = run_gate(["validate"], env=self.env)
        assert result.returncode != 0, f"validate should fail with invalid signature: {result.stdout}"

    def test_key_missing(self):
        """Missing key should fail validate."""
        run_gate(["init"], env=self.env)
        os.remove(self.key_file)
        result = run_gate(["validate"], env=self.env)
        assert result.returncode != 0, f"validate should fail when key is missing: {result.stdout}"

    def test_phase_not_approved(self):
        """Unapproved phase should fail when chain is empty."""
        run_gate(["init"], env=self.env)
        result = run_gate(["validate"], env=self.env)
        assert result.returncode != 0, f"empty log should fail: {result.stdout}"

    def test_log_truncated(self):
        """Truncated log should break chain (simulate by modifying previous_hash)."""
        run_gate(["init"], env=self.env)
        run_gate(["approve", "--phase", "briefing"], env=self.env)
        run_gate(["approve", "--phase", "spec"], env=self.env)
        with open(self.log_file) as f:
            lines = f.readlines()
        entry2 = json.loads(lines[1])
        entry2["payload"]["previous_hash"] = "0" * 64
        with open(self.log_file, "w") as f:
            f.write(json.dumps(lines[0]) + json.dumps(entry2) + "\n")
        result = run_gate(["validate"], env=self.env)
        assert result.returncode != 0, f"validate should fail when log is truncated: {result.stdout}"

    def test_status_strict_on_valid_chain(self):
        """Status --strict should pass on valid chain."""
        run_gate(["init"], env=self.env)
        run_gate(["approve", "--phase", "briefing"], env=self.env)
        run_gate(["approve", "--phase", "spec"], env=self.env)
        result = run_gate(["status", "--strict"], env=self.env)
        assert result.returncode == 0, f"status --strict should pass: {result.stderr}"

    def test_approve_creates_signature(self):
        """Approve should create entry with valid signature."""
        import hmac, hashlib, base64
        run_gate(["init"], env=self.env)
        result = run_gate(["approve", "--phase", "briefing"], env=self.env)
        assert result.returncode == 0
        with open(self.log_file) as f:
            entry = json.loads(f.readline())
        assert "signature" in entry
        assert "payload" in entry
        payload_str = json.dumps(entry["payload"], separators=(",", ":"))
        with open(self.key_file, "rb") as kf:
            key = kf.read()
        expected = base64.b64encode(hmac.new(key, payload_str.encode(), hashlib.sha256).digest()).decode()
        assert entry["signature"] == expected, "signature should match"