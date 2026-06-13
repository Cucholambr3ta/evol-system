"""Tests for EDMS Memory v2.0 — dialectic user model (Gap 3)."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evol_memory_v2.user_model import UserModelStore, MIN_EVIDENCE_TO_FIX


def _um():
    return UserModelStore(tempfile.mkdtemp())


class TestUserModelStore:
    def test_default_profile(self):
        um = _um()
        m = um.get()
        assert m["preferences"] == {}
        assert m["triggers"] == []
        assert m["version"] == 0

    def test_set_preference(self):
        um = _um()
        um.set_preference("format", "markdown sin emojis")
        assert um.get()["preferences"]["format"] == "markdown sin emojis"

    def test_version_increments_on_save(self):
        um = _um()
        um.set_preference("a", 1)
        um.set_preference("b", 2)
        assert um.get()["version"] == 2

    def test_add_trigger(self):
        um = _um()
        um.add_trigger("caveman", "modo terse", "usuario invoca /caveman")
        triggers = um.get()["triggers"]
        assert len(triggers) == 1
        assert triggers[0]["trigger"] == "caveman"
        assert triggers[0]["response"] == "modo terse"

    def test_add_trigger_replaces_same_key(self):
        um = _um()
        um.add_trigger("quick", "mvp", "")
        um.add_trigger("quick", "minimal viable", "")
        triggers = um.get()["triggers"]
        assert len(triggers) == 1
        assert triggers[0]["response"] == "minimal viable"

    def test_detect_triggers(self):
        um = _um()
        um.add_trigger("caveman", "modo terse")
        um.add_trigger("optimize", "performance focus")
        found = um.detect_triggers("por favor activa caveman ahora")
        assert len(found) == 1
        assert found[0]["trigger"] == "caveman"

    def test_detect_triggers_none(self):
        um = _um()
        um.add_trigger("caveman", "modo terse")
        assert um.detect_triggers("texto sin disparadores") == []

    def test_decision_pattern_evidence_based_confidence(self):
        um = _um()
        # snapshot scalars — observe_decision_pattern returns the live entry
        p1 = um.observe_decision_pattern("exige cero deuda", evidence_id="s1")
        conf1, fixed1 = p1["confidence"], p1["fixed"]
        assert fixed1 is False
        assert conf1 == 0.75  # 0.5 + 0.25*1
        p2 = um.observe_decision_pattern("exige cero deuda", evidence_id="s2")
        assert p2["fixed"] is True       # 2 evidence ids >= MIN_EVIDENCE_TO_FIX
        assert p2["confidence"] > conf1

    def test_decision_pattern_dedupes_evidence(self):
        um = _um()
        um.observe_decision_pattern("p", evidence_id="s1")
        entry = um.observe_decision_pattern("p", evidence_id="s1")  # same evidence
        assert entry["evidence_ids"] == ["s1"]
        assert entry["fixed"] is False

    def test_fixed_patterns_filter(self):
        um = _um()
        um.observe_decision_pattern("weak", evidence_id="s1")
        um.observe_decision_pattern("strong", evidence_id="s1")
        um.observe_decision_pattern("strong", evidence_id="s2")
        fixed = um.fixed_patterns()
        assert len(fixed) == 1
        assert fixed[0]["pattern"] == "strong"

    def test_confidence_capped(self):
        um = _um()
        for i in range(10):
            entry = um.observe_decision_pattern("p", evidence_id=f"s{i}")
        assert entry["confidence"] <= 0.99

    def test_wake_up_summary_contains_signals(self):
        um = _um()
        um.set_preference("format", "markdown")
        um.add_trigger("caveman", "terse")
        um.observe_decision_pattern("cero deuda", evidence_id="s1")
        um.observe_decision_pattern("cero deuda", evidence_id="s2")
        summary = um.wake_up_summary()
        assert "markdown" in summary
        assert "caveman" in summary
        assert "cero deuda" in summary

    def test_wake_up_summary_empty(self):
        assert "vacio" in _um().wake_up_summary()

    def test_persistence_across_instances(self):
        d = tempfile.mkdtemp()
        um1 = UserModelStore(d)
        um1.set_preference("format", "markdown")
        um1.add_trigger("caveman", "terse")
        # New instance reads from disk
        um2 = UserModelStore(d)
        assert um2.get()["preferences"]["format"] == "markdown"
        assert len(um2.get()["triggers"]) == 1

    def test_stats(self):
        um = _um()
        um.set_preference("a", 1)
        um.add_trigger("t", "r")
        um.observe_decision_pattern("p", evidence_id="s1")
        s = um.stats()
        assert s["preferences"] == 1
        assert s["triggers"] == 1
        assert s["decision_patterns"] == 1
        assert s["fixed_patterns"] == 0

    def test_min_evidence_constant(self):
        assert MIN_EVIDENCE_TO_FIX == 2
