import os, sys, sqlite3, tempfile, shutil, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts._evol_common import get_state_db

class TestStateHermetic:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp(prefix="test_state_")

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def run_state(self, args, env=None):
        import subprocess
        full_env = dict(os.environ)
        if env:
            full_env.update(env)
        result = subprocess.run(
            [sys.executable, "scripts/evol-state.py"] + args,
            capture_output=True, text=True, env=full_env
        )
        return result

    def test_init_creates_db(self):
        """init should create database in EVOL_STATE_DB override."""
        db_path = os.path.join(self.tmpdir, "state.db")
        env = {"EVOL_STATE_DB": db_path}
        result = self.run_state(["init"], env=env)
        assert result.returncode == 0, result.stderr
        assert os.path.exists(db_path), f"DB should exist at {db_path}"
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        assert "instincts" in tables
        assert "agent_lifecycle" in tables
        assert "research_proposals" in tables

    def test_record_and_list_instinct(self):
        """record-instinct and list should work with temp DB."""
        db_path = os.path.join(self.tmpdir, "state.db")
        env = {"EVOL_STATE_DB": db_path}
        self.run_state(["init"], env=env)
        result = self.run_state(["record-instinct", "--pattern", "test-pattern",
                                  "--confidence", "0.8", "--source", "test"], env=env)
        assert result.returncode == 0, result.stderr
        result = self.run_state(["list"], env=env)
        assert result.returncode == 0
        assert "test-pattern" in result.stdout

    def test_stats(self):
        """stats should work with temp DB."""
        db_path = os.path.join(self.tmpdir, "state.db")
        env = {"EVOL_STATE_DB": db_path}
        self.run_state(["init"], env=env)
        result = self.run_state(["stats"], env=env)
        assert result.returncode == 0, result.stderr
        assert "instincts:" in result.stdout

    def test_evolve_status(self):
        """evolve status should work with temp DB."""
        db_path = os.path.join(self.tmpdir, "state.db")
        env = {"EVOL_STATE_DB": db_path}
        self.run_state(["init"], env=env)
        result = self.run_state(["evolve"], env=env)
        assert result.returncode == 0, result.stderr

    def test_list_uses_state_db_override(self):
        """list should use EVOL_STATE_DB, not hardcoded path."""
        db_path = os.path.join(self.tmpdir, "mydb.db")
        env = {"EVOL_STATE_DB": db_path}
        self.run_state(["init"], env=env)
        self.run_state(["record-instinct", "--pattern", "override-test"], env=env)
        actual_db = get_state_db.__wrapped__ if hasattr(get_state_db, '__wrapped__') else None
        result = self.run_state(["list"], env=env)
        assert "override-test" in result.stdout

    def test_init_idempotent(self):
        """Multiple init calls should not fail."""
        db_path = os.path.join(self.tmpdir, "state.db")
        env = {"EVOL_STATE_DB": db_path}
        r1 = self.run_state(["init"], env=env)
        assert r1.returncode == 0
        r2 = self.run_state(["init"], env=env)
        assert r2.returncode == 0

    def test_prune(self):
        """prune should work with temp DB."""
        db_path = os.path.join(self.tmpdir, "state.db")
        env = {"EVOL_STATE_DB": db_path}
        self.run_state(["init"], env=env)
        result = self.run_state(["prune", "--days", "30"], env=env)
        assert result.returncode == 0, result.stderr

    def test_parallel_safe(self):
        """Two parallel init calls should not corrupt DB."""
        import threading, time
        db_path = os.path.join(self.tmpdir, "parallel.db")
        env = {"EVOL_STATE_DB": db_path}
        errors = []

        def init_and_record(i):
            r = self.run_state(["init"], env=env)
            if r.returncode != 0:
                errors.append(f"init failed: {r.stderr}")
            r = self.run_state(["record-instinct", "--pattern", f"parallel-{i}"], env=env)
            if r.returncode != 0:
                errors.append(f"record failed: {r.stderr}")

        threads = [threading.Thread(target=init_and_record, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Parallel ops had errors: {errors}"
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM instincts")
        count = cur.fetchone()[0]
        conn.close()
        assert count >= 4, f"Should have at least 4 records, got {count}"