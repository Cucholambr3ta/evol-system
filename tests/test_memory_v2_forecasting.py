"""Tests for EDMS Memory v2.0 — forecasting / predictive memories (Gap 1)."""

import sys
import tempfile
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evol_memory_v2.forecasting import ForecastEngine, Prediction, _sprint_of
from evol_memory_v2.dreaming import DreamingEngine, DreamConfig
from evol_memory_v2.reflection import MemoryItem


def _mem(id, text, tipo=None, sprint=None):
    meta = {}
    if tipo:
        meta["tipo"] = tipo
    if sprint:
        meta["sprint"] = sprint
    return MemoryItem(id=id, text=text, metadata=meta)


# ============================================================================
# ForecastEngine
# ============================================================================

class TestForecastEngine:
    def test_empty_yields_nothing(self):
        assert ForecastEngine().forecast([]) == []

    def test_single_occurrence_below_threshold(self):
        mems = [_mem("a", "QA de SecDD", tipo="leccion", sprint="5")]
        assert ForecastEngine(min_occurrences=2).forecast(mems) == []

    def test_recurring_discipline_predicted(self):
        mems = [
            _mem("a", "QA de SecDD sprint-5", tipo="artefacto", sprint="5"),
            _mem("b", "controles SecDD sprint-6", tipo="artefacto", sprint="6"),
        ]
        preds = ForecastEngine().forecast(mems)
        disc = [p for p in preds if p.metadata["kind"] == "discipline"]
        assert len(disc) == 1
        assert disc[0].metadata["label"] == "secdd"
        assert disc[0].evidence_ids == ["a", "b"]

    def test_recurring_risk_predicted(self):
        mems = [
            _mem("a", "riesgo deuda sprint-5", tipo="riesgo", sprint="5"),
            _mem("b", "riesgo deuda sprint-6", tipo="riesgo", sprint="6"),
        ]
        preds = ForecastEngine().forecast(mems)
        assert any(p.metadata["kind"] == "riesgo" for p in preds)

    def test_gate_failure_predicted(self):
        mems = [
            _mem("a", "el gate de plan fallo por grill", tipo="leccion", sprint="5"),
            _mem("b", "gate bloqueado en fase plan", tipo="leccion", sprint="6"),
        ]
        preds = ForecastEngine().forecast(mems)
        assert any(p.metadata["kind"] == "gate" for p in preds)

    def test_confidence_grows_with_occurrences(self):
        few = [
            _mem("a", "riesgo X sprint-5", tipo="riesgo", sprint="5"),
            _mem("b", "riesgo X sprint-6", tipo="riesgo", sprint="6"),
        ]
        many = few + [
            _mem("c", "riesgo X sprint-7", tipo="riesgo", sprint="7"),
            _mem("d", "riesgo X sprint-8", tipo="riesgo", sprint="8"),
        ]
        c_few = ForecastEngine().forecast(few)[0].confidence
        c_many = ForecastEngine().forecast(many)[0].confidence
        assert c_many > c_few

    def test_confidence_capped(self):
        mems = [
            _mem(f"m{i}", f"riesgo Y sprint-{i}", tipo="riesgo", sprint=str(i))
            for i in range(10)
        ]
        assert ForecastEngine().forecast(mems)[0].confidence <= 0.99

    def test_min_confidence_filter(self):
        mems = [
            _mem("a", "riesgo Z sprint-5", tipo="riesgo", sprint="5"),
            _mem("b", "riesgo Z sprint-6", tipo="riesgo", sprint="6"),
        ]
        # threshold above what 2 occurrences can reach
        assert ForecastEngine(min_confidence=0.999).forecast(mems) == []

    def test_predictions_sorted_by_confidence(self):
        mems = [
            _mem("r1", "riesgo A sprint-5", tipo="riesgo", sprint="5"),
            _mem("r2", "riesgo A sprint-6", tipo="riesgo", sprint="6"),
            _mem("r3", "riesgo A sprint-7", tipo="riesgo", sprint="7"),
            _mem("l1", "leccion B sprint-5", tipo="leccion", sprint="5"),
            _mem("l2", "leccion B sprint-6", tipo="leccion", sprint="6"),
        ]
        preds = ForecastEngine().forecast(mems)
        confs = [p.confidence for p in preds]
        assert confs == sorted(confs, reverse=True)

    def test_prediction_atom_metadata(self):
        p = Prediction(id="p1", content="x", confidence=0.8, horizon="next sprint",
                        evidence_ids=["a"])
        meta = p.to_atom_metadata()
        assert meta["tipo"] == "prediction"
        assert meta["confidence"] == 0.8
        assert meta["source"] == "forecasting"

    def test_stable_id_for_same_pattern(self):
        e = ForecastEngine()
        assert e._make_id("riesgo", "riesgo") == e._make_id("riesgo", "riesgo")

    def test_stats(self):
        mems = [
            _mem("a", "riesgo W sprint-5", tipo="riesgo", sprint="5"),
            _mem("b", "riesgo W sprint-6", tipo="riesgo", sprint="6"),
        ]
        e = ForecastEngine()
        e.forecast(mems)
        s = e.stats()
        assert s["total_predictions"] == 1
        assert "riesgo" in s["by_kind"]


class TestSprintExtraction:
    def test_from_metadata(self):
        assert _sprint_of(_mem("a", "x", sprint="7")) == "sprint-7"

    def test_from_text(self):
        assert _sprint_of(_mem("a", "trabajo en sprint-12 hoy")) == "sprint-12"

    def test_none_when_absent(self):
        assert _sprint_of(_mem("a", "sin marcador")) is None


# ============================================================================
# Dreaming integration (Phase 3)
# ============================================================================

class TestDreamingForecastIntegration:
    def test_forecasting_off_by_default(self):
        engine = DreamingEngine()
        mems = [
            _mem("a", "riesgo deuda sprint-5", tipo="riesgo", sprint="5"),
            _mem("b", "riesgo deuda sprint-6", tipo="riesgo", sprint="6"),
        ]
        engine.dream(mems)
        assert engine.get_predictions() == []
        # no forecasting phase logged
        phases = [p["phase"] for p in engine.get_latest_session().phases]
        assert "forecasting" not in phases

    def test_forecasting_on_produces_predictions(self):
        engine = DreamingEngine(DreamConfig(enable_forecasting=True))
        mems = [
            _mem("a", "riesgo deuda sprint-5", tipo="riesgo", sprint="5"),
            _mem("b", "riesgo deuda sprint-6", tipo="riesgo", sprint="6"),
        ]
        engine.dream(mems)
        assert len(engine.get_predictions()) >= 1
        phases = [p["phase"] for p in engine.get_latest_session().phases]
        assert "forecasting" in phases

    def test_forecasting_phase_logged_with_counts(self):
        engine = DreamingEngine(DreamConfig(enable_forecasting=True))
        mems = [
            _mem("a", "riesgo X sprint-5", tipo="riesgo", sprint="5"),
            _mem("b", "riesgo X sprint-6", tipo="riesgo", sprint="6"),
        ]
        engine.dream(mems)
        fc = [p for p in engine.get_latest_session().phases if p["phase"] == "forecasting"][0]
        assert fc["items_in"] == 2
        assert fc["items_out"] >= 1

    def test_predictions_survive_save_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dream.json"
            engine = DreamingEngine(DreamConfig(enable_forecasting=True))
            mems = [
                _mem("a", "riesgo deuda sprint-5", tipo="riesgo", sprint="5"),
                _mem("b", "riesgo deuda sprint-6", tipo="riesgo", sprint="6"),
            ]
            engine.dream(mems)
            n = len(engine.get_predictions())
            engine.save(path)

            loaded = DreamingEngine.load(path)
            assert len(loaded.get_predictions()) == n
            assert loaded.get_predictions()[0].source == "forecasting"

    def test_get_predictions_min_confidence(self):
        engine = DreamingEngine(DreamConfig(enable_forecasting=True))
        mems = [
            _mem("a", "riesgo deuda sprint-5", tipo="riesgo", sprint="5"),
            _mem("b", "riesgo deuda sprint-6", tipo="riesgo", sprint="6"),
        ]
        engine.dream(mems)
        assert engine.get_predictions(min_confidence=1.0) == []
