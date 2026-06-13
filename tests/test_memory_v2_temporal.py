"""Tests for EDMS Memory v2.0 — temporal recency signal in HybridRetriever (Gap 4)."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evol_memory_v2.hybrid_retriever import (
    DEFAULT_HALF_LIFE_DAYS,
    HALF_LIFE_BY_TIPO,
    HybridRetriever,
    _parse_timestamp,
    _temporal_weight,
)

NOW = datetime(2026, 6, 13, tzinfo=timezone.utc)


# ============================================================================
# Pure function: _temporal_weight
# ============================================================================

class TestTemporalWeight:
    def test_fresh_is_one(self):
        assert _temporal_weight(NOW.isoformat(), 90, now=NOW) == 1.0

    def test_half_life_is_half(self):
        old = (NOW - timedelta(days=90)).isoformat()
        assert abs(_temporal_weight(old, 90, now=NOW) - 0.5) < 1e-6

    def test_two_half_lives_is_quarter(self):
        old = (NOW - timedelta(days=180)).isoformat()
        assert abs(_temporal_weight(old, 90, now=NOW) - 0.25) < 1e-6

    def test_missing_timestamp_is_neutral(self):
        assert _temporal_weight(None, 90, now=NOW) == 1.0
        assert _temporal_weight("", 90, now=NOW) == 1.0

    def test_unparseable_timestamp_is_neutral(self):
        assert _temporal_weight("not-a-date", 90, now=NOW) == 1.0

    def test_zero_half_life_disables(self):
        old = (NOW - timedelta(days=365)).isoformat()
        assert _temporal_weight(old, 0, now=NOW) == 1.0

    def test_future_timestamp_clamped_to_one(self):
        future = (NOW + timedelta(days=30)).isoformat()
        assert _temporal_weight(future, 90, now=NOW) == 1.0

    def test_weight_is_monotonic_decreasing(self):
        w0 = _temporal_weight((NOW - timedelta(days=10)).isoformat(), 90, now=NOW)
        w1 = _temporal_weight((NOW - timedelta(days=60)).isoformat(), 90, now=NOW)
        assert w0 > w1 > 0.0


class TestParseTimestamp:
    def test_iso_with_z(self):
        dt = _parse_timestamp("2026-06-13T10:00:00Z")
        assert dt is not None and dt.tzinfo is not None

    def test_naive_iso_gets_utc(self):
        dt = _parse_timestamp("2026-06-13T10:00:00")
        assert dt is not None and dt.tzinfo == timezone.utc

    def test_epoch_float(self):
        assert _parse_timestamp(1_700_000_000.0) is not None

    def test_none(self):
        assert _parse_timestamp(None) is None


# ============================================================================
# HybridRetriever integration
# ============================================================================

class TestHybridRetrieverTemporal:
    def test_decay_zero_is_backward_compatible(self):
        """temporal_decay=0 must yield identical scores to the same corpus
        retrieved with decay fully on but timestamps absent — i.e. the
        temporal branch contributes a 1.0 multiplier and changes nothing."""
        old = (NOW - timedelta(days=300)).isoformat()

        def build(decay, with_ts):
            r = HybridRetriever(temporal_decay=decay, use_vector=False)
            meta_a = {"tipo": "decision"}
            meta_b = {"tipo": "riesgo"}
            if with_ts:
                meta_a["created_at"] = old
                meta_b["created_at"] = old
            r.add_document("a", "alpha beta gamma", meta_a)
            r.add_document("b", "alpha beta gamma", meta_b)
            return {x.id: x.score for x in r.search("alpha beta gamma")}

        off = build(0.0, with_ts=True)
        on_no_ts = build(1.0, with_ts=False)
        # decay off == decay on but no timestamps (both multiply by 1.0)
        assert off.keys() == on_no_ts.keys()
        for doc_id in off:
            assert abs(off[doc_id] - on_no_ts[doc_id]) < 1e-12

    def test_decay_one_prefers_recent(self):
        old = (NOW - timedelta(days=120)).isoformat()
        fresh = NOW.isoformat()
        r = HybridRetriever(temporal_decay=1.0, use_vector=False)
        r.add_document("old", "foo bar baz", {"tipo": "decision", "created_at": old})
        r.add_document("new", "foo bar baz", {"tipo": "decision", "created_at": fresh})
        results = r.search("foo bar baz")
        assert results[0].id == "new"
        assert results[0].score > results[1].score

    def test_half_life_by_tipo_applied(self):
        """At equal age, longer half-life tipo outranks shorter one."""
        old = (NOW - timedelta(days=90)).isoformat()
        r = HybridRetriever(temporal_decay=1.0, use_vector=False)
        r.add_document("dec", "foo bar baz", {"tipo": "decision", "created_at": old})  # hl 365
        r.add_document("risk", "foo bar baz", {"tipo": "riesgo", "created_at": old})   # hl 60
        results = r.search("foo bar baz")
        assert results[0].id == "dec"

    def test_unknown_tipo_uses_default_half_life(self):
        old = (NOW - timedelta(days=30)).isoformat()
        r = HybridRetriever(temporal_decay=1.0, use_vector=False)
        r.add_document("x", "foo bar baz", {"tipo": "weird", "created_at": old})
        # Should not raise; default half-life applies
        results = r.search("foo bar baz")
        assert len(results) == 1
        assert 0.0 < results[0].score < 1.0

    def test_half_life_override(self):
        r = HybridRetriever(
            temporal_decay=1.0, use_vector=False,
            half_life_by_tipo={"decision": 1.0},
        )
        assert r.half_life_by_tipo["decision"] == 1.0
        # Other defaults preserved
        assert r.half_life_by_tipo["riesgo"] == HALF_LIFE_BY_TIPO["riesgo"]

    def test_temporal_decay_clamped(self):
        assert HybridRetriever(temporal_decay=5.0).temporal_decay == 1.0
        assert HybridRetriever(temporal_decay=-1.0).temporal_decay == 0.0

    def test_stats_exposes_decay(self):
        r = HybridRetriever(temporal_decay=0.7, use_vector=False)
        assert r.stats()["config"]["temporal_decay"] == 0.7

    def test_missing_created_at_does_not_penalize(self):
        """A doc without a timestamp keeps a full 1.0 recency multiplier."""
        r = HybridRetriever(temporal_decay=1.0, use_vector=False)
        assert r._recency_multiplier({"tipo": "decision"}) == 1.0

    def test_recency_multiplier_blends_by_decay(self):
        """Multiplier interpolates between 1.0 (decay 0) and raw weight (decay 1)."""
        old = (NOW - timedelta(days=365)).isoformat()  # decision hl=365 -> raw 0.5
        meta = {"tipo": "decision", "created_at": old}
        full = HybridRetriever(temporal_decay=1.0, use_vector=False)
        half = HybridRetriever(temporal_decay=0.5, use_vector=False)
        off = HybridRetriever(temporal_decay=0.0, use_vector=False)
        m_full = full._recency_multiplier(meta)
        assert abs(m_full - 0.5) < 0.05            # ~raw weight at one half-life
        assert off._recency_multiplier(meta) == 1.0
        assert m_full < half._recency_multiplier(meta) < 1.0

    def test_default_half_life_constant(self):
        assert DEFAULT_HALF_LIFE_DAYS == 90.0
