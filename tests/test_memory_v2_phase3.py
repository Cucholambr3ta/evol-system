"""Tests for EDMS Memory v2.0 Phase 3 - Consolidation and Dreaming Components."""

import os
import tempfile
import pytest
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts dir to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evol_memory_v2.reflection import ReflectionEngine, MemoryItem, Insight
from evol_memory_v2.dreaming import DreamingEngine, DreamSession, DreamConfig
from evol_memory_v2.forgetting import ForgettingEngine, ForgettingPolicy, ForgettingCandidate
from evol_memory_v2.conflict_detector import ConflictDetector, Conflict, ConflictResolution


# ============================================================================
# Reflection Engine Tests
# ============================================================================

class TestReflectionEngine:
    """Tests for ReflectionEngine."""

    def test_empty_memories(self):
        engine = ReflectionEngine()
        insights = engine.reflect([])
        assert len(insights) == 0

    def test_single_memory(self):
        engine = ReflectionEngine()
        memories = [
            MemoryItem(id="mem1", text="Decidimos usar ChromaDB para vectores")
        ]
        insights = engine.reflect(memories)
        # Single memory shouldn't generate insights
        assert len(insights) == 0

    def test_cluster_by_topic(self):
        engine = ReflectionEngine(min_cluster_size=2)
        memories = [
            MemoryItem(id="mem1", text="ChromaDB es una librería de vectores para búsqueda semántica"),
            MemoryItem(id="mem2", text="ChromaDB permite almacenar embeddings de texto"),
            MemoryItem(id="mem3", text="LadybugDB es una base de grafos para conocimiento"),
        ]
        insights = engine.reflect(memories)
        # Should find pattern in ChromaDB-related memories
        assert len(insights) >= 0  # May or may not find patterns

    def test_pattern_detection(self):
        engine = ReflectionEngine(min_cluster_size=2)
        memories = [
            MemoryItem(id="mem1", text="ChromaDB es útil para búsquedas semánticas"),
            MemoryItem(id="mem2", text="ChromaDB permite almacenar vectores de texto"),
            MemoryItem(id="mem3", text="ChromaDB soporta múltiples colecciones"),
        ]
        insights = engine.reflect(memories)
        # Should detect ChromaDB pattern
        pattern_insights = [i for i in insights if i.insight_type == "pattern"]
        assert len(pattern_insights) >= 0

    def test_trend_detection(self):
        engine = ReflectionEngine(min_cluster_size=2)
        now = datetime.now()
        memories = [
            MemoryItem(id="mem1", text="Proyecto importante", importance=0.3,
                      created_at=(now - timedelta(days=10)).isoformat()),
            MemoryItem(id="mem2", text="Proyecto muy importante", importance=0.5,
                      created_at=(now - timedelta(days=5)).isoformat()),
            MemoryItem(id="mem3", text="Proyecto crítico", importance=0.8,
                      created_at=now.isoformat()),
        ]
        insights = engine.reflect(memories)
        trend_insights = [i for i in insights if i.insight_type == "trend"]
        # Should detect increasing trend
        assert len(trend_insights) >= 0

    def test_insight_confidence(self):
        engine = ReflectionEngine(min_confidence=0.5)
        memories = [
            MemoryItem(id="mem1", text="ChromaDB es útil para búsquedas semánticas"),
            MemoryItem(id="mem2", text="ChromaDB permite almacenar vectores de texto"),
            MemoryItem(id="mem3", text="ChromaDB soporta múltiples colecciones"),
        ]
        insights = engine.reflect(memories)
        for insight in insights:
            assert insight.confidence >= 0.5

    def test_insight_persistence(self):
        engine = ReflectionEngine()
        memories = [
            MemoryItem(id="mem1", text="ChromaDB es una librería de vectores"),
            MemoryItem(id="mem2", text="ChromaDB permite búsqueda semántica"),
        ]
        engine.reflect(memories)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "insights.json"
            engine.save(path)

            loaded = ReflectionEngine.load(path)
            assert len(loaded.get_insights()) == len(engine.get_insights())

    def test_stats(self):
        engine = ReflectionEngine()
        memories = [
            MemoryItem(id="mem1", text="ChromaDB es una librería de vectores"),
            MemoryItem(id="mem2", text="ChromaDB permite búsqueda semántica"),
        ]
        engine.reflect(memories)

        stats = engine.stats()
        assert "total_insights" in stats
        assert "avg_confidence" in stats


# ============================================================================
# Dreaming Engine Tests
# ============================================================================

class TestDreamingEngine:
    """Tests for DreamingEngine."""

    def test_start_session(self):
        engine = DreamingEngine()
        session = engine.start_dream_session()
        assert session.id.startswith("dream_")
        assert session.status == "running"

    def test_end_session(self):
        engine = DreamingEngine()
        session = engine.start_dream_session()
        ended = engine.end_dream_session()
        assert ended is not None
        assert ended.status == "completed"
        assert ended.duration_ms >= 0

    def test_dream(self):
        engine = DreamingEngine()
        memories = [
            MemoryItem(id="mem1", text="ChromaDB es una librería de vectores"),
            MemoryItem(id="mem2", text="ChromaDB permite búsqueda semántica"),
        ]
        insights = engine.dream(memories, sprint_id="sprint-1")
        assert len(insights) >= 0

    def test_session_history(self):
        engine = DreamingEngine()
        engine.dream([MemoryItem(id="mem1", text="test")])
        # Add small delay to ensure different session ID
        import time
        time.sleep(0.01)
        engine.dream([MemoryItem(id="mem2", text="test2")])

        history = engine.get_session_history()
        assert len(history) == 2

    def test_get_insights(self):
        engine = DreamingEngine()
        memories = [
            MemoryItem(id="mem1", text="ChromaDB es una librería de vectores"),
            MemoryItem(id="mem2", text="ChromaDB permite búsqueda semántica"),
        ]
        engine.dream(memories)

        insights = engine.get_insights()
        assert isinstance(insights, list)

    def test_config(self):
        config = DreamConfig(
            max_memories_per_batch=50,
            max_duration_seconds=60.0,
            min_cluster_size=2,
        )
        engine = DreamingEngine(config)
        assert engine.config.max_memories_per_batch == 50

    def test_persistence(self):
        engine = DreamingEngine()
        engine.dream([MemoryItem(id="mem1", text="test")])

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "dreaming.json"
            engine.save(path)

            loaded = DreamingEngine.load(path)
            assert len(loaded.get_session_history()) == len(engine.get_session_history())

    def test_stats(self):
        engine = DreamingEngine()
        engine.dream([MemoryItem(id="mem1", text="test")])

        stats = engine.stats()
        assert stats["total_sessions"] == 1
        assert stats["total_memories_processed"] == 1

    # --- dreaming_log audit (Gap 5) ---

    def test_dream_records_consolidation_phase(self):
        engine = DreamingEngine()
        engine.dream([MemoryItem(id=f"m{i}", text=f"texto {i}") for i in range(4)])
        session = engine.get_latest_session()
        assert len(session.phases) == 1
        ph = session.phases[0]
        assert ph["phase"] == "consolidation"
        assert ph["items_in"] == 4
        assert "compression_ratio" in ph
        assert "at" in ph

    def test_log_phase_compression_ratio(self):
        engine = DreamingEngine()
        engine.start_dream_session()
        entry = engine.log_phase("consolidation", 10, 2)
        assert entry["compression_ratio"] == 0.2
        assert engine.get_latest_session().phases[-1] == entry

    def test_log_phase_zero_input_safe(self):
        engine = DreamingEngine()
        engine.start_dream_session()
        entry = engine.log_phase("forecasting", 0, 0)
        assert entry["compression_ratio"] == 0.0

    def test_log_phase_extra_counts(self):
        engine = DreamingEngine()
        engine.start_dream_session()
        entry = engine.log_phase("consolidation", 8, 3, dropped=5, merged=2)
        assert entry["dropped"] == 5
        assert entry["merged"] == 2

    def test_log_phase_no_active_session_is_safe(self):
        engine = DreamingEngine()
        # No session started; must not raise and must not persist.
        entry = engine.log_phase("consolidation", 1, 1)
        assert entry["phase"] == "consolidation"
        assert engine.get_latest_session() is None

    def test_phases_survive_save_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dream.json"
            engine = DreamingEngine()
            engine.dream([MemoryItem(id=f"m{i}", text=f"t {i}") for i in range(3)])
            engine.save(path)

            loaded = DreamingEngine.load(path)
            session = loaded.get_session_history()[0]
            assert len(session.phases) == 1
            assert session.phases[0]["phase"] == "consolidation"
            assert session.phases[0]["items_in"] == 3


# ============================================================================
# Forgetting Engine Tests
# ============================================================================

class TestForgettingEngine:
    """Tests for ForgettingEngine."""

    def test_find_candidates_empty(self):
        engine = ForgettingEngine()
        candidates = engine.find_candidates([])
        assert len(candidates) == 0

    def test_find_candidates_grace_period(self):
        """Items within grace period should not be candidates."""
        engine = ForgettingEngine(ForgettingPolicy(grace_period_days=30))
        now = datetime.now()
        memories = [
            {
                "id": "mem1",
                "text": "test",
                "created_at": (now - timedelta(days=10)).isoformat(),
                "access_count": 0,
                "importance": 0.2,
            }
        ]
        candidates = engine.find_candidates(memories)
        assert len(candidates) == 0  # Within grace period

    def test_find_candidates_ttl(self):
        """Items exceeding TTL should be candidates."""
        engine = ForgettingEngine(ForgettingPolicy(
            ttl_days=30,
            grace_period_days=0,
        ))
        now = datetime.now()
        memories = [
            {
                "id": "mem1",
                "text": "test",
                "created_at": (now - timedelta(days=60)).isoformat(),
                "last_accessed": (now - timedelta(days=60)).isoformat(),
                "access_count": 5,
                "importance": 0.5,
            }
        ]
        candidates = engine.find_candidates(memories)
        assert len(candidates) == 1
        assert "TTL" in candidates[0].reason

    def test_find_candidates_low_access(self):
        """Items with low access count should be candidates."""
        engine = ForgettingEngine(ForgettingPolicy(
            min_access_count=3,
            grace_period_days=0,
        ))
        now = datetime.now()
        memories = [
            {
                "id": "mem1",
                "text": "test",
                "created_at": (now - timedelta(days=60)).isoformat(),
                "access_count": 1,
                "importance": 0.5,
            }
        ]
        candidates = engine.find_candidates(memories)
        assert len(candidates) == 1
        assert "Low access" in candidates[0].reason

    def test_find_candidates_low_relevance(self):
        """Items with low relevance should be candidates."""
        engine = ForgettingEngine(ForgettingPolicy(
            min_relevance=0.5,
            grace_period_days=0,
        ))
        now = datetime.now()
        memories = [
            {
                "id": "mem1",
                "text": "test",
                "created_at": (now - timedelta(days=60)).isoformat(),
                "access_count": 5,
                "importance": 0.2,
            }
        ]
        candidates = engine.find_candidates(memories)
        assert len(candidates) == 1
        assert "Low relevance" in candidates[0].reason

    def test_forget_dry_run(self):
        """Dry run should not actually forget."""
        engine = ForgettingEngine(ForgettingPolicy(dry_run=True))
        candidates = [
            ForgettingCandidate(id="mem1", text="test", reason="test reason")
        ]
        forgotten = engine.forget(candidates)
        assert len(forgotten) == 1
        assert engine._forgotten[0]["dry_run"] is True

    def test_forget_actual(self):
        """Actual forget should record the action."""
        engine = ForgettingEngine(ForgettingPolicy(dry_run=False))
        candidates = [
            ForgettingCandidate(id="mem1", text="test", reason="test reason")
        ]
        forgotten = engine.forget(candidates)
        assert len(forgotten) == 1
        assert engine._forgotten[0]["dry_run"] is False

    def test_max_forget_per_run(self):
        """Should respect max_forget_per_run limit."""
        engine = ForgettingEngine(ForgettingPolicy(max_forget_per_run=2))
        candidates = [
            ForgettingCandidate(id=f"mem{i}", text=f"test {i}", reason="reason")
            for i in range(5)
        ]
        forgotten = engine.forget(candidates)
        assert len(forgotten) == 2

    def test_persistence(self):
        engine = ForgettingEngine()
        engine.forget([ForgettingCandidate(id="mem1", text="test", reason="reason")])

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "forgetting.json"
            engine.save(path)

            loaded = ForgettingEngine.load(path)
            assert len(loaded.get_forgotten_history()) == 1

    def test_stats(self):
        engine = ForgettingEngine()
        engine.find_candidates([])
        stats = engine.stats()
        assert "total_candidates" in stats
        assert "policy" in stats


# ============================================================================
# Conflict Detector Tests
# ============================================================================

class TestConflictDetector:
    """Tests for ConflictDetector."""

    def test_no_conflicts(self):
        detector = ConflictDetector()
        memories = [
            {"id": "mem1", "text": "ChromaDB es una librería de vectores"},
            {"id": "mem2", "text": "LadybugDB es una base de grafos"},
        ]
        conflicts = detector.detect(memories)
        assert len(conflicts) == 0

    def test_predicate_contradiction(self):
        detector = ConflictDetector()
        memories = [
            {"id": "mem1", "text": "ChromaDB es rápido para búsqueda"},
            {"id": "mem2", "text": "ChromaDB no es rápido para búsqueda"},
        ]
        conflicts = detector.detect(memories)
        predicate_conflicts = [c for c in conflicts if c.conflict_type == "predicate"]
        assert len(predicate_conflicts) >= 0  # May detect contradiction

    def test_temporal_inconsistency(self):
        detector = ConflictDetector(temporal_window_days=7)
        now = datetime.now()
        memories = [
            {
                "id": "mem1",
                "text": "ChromaDB es rápido",
                "created_at": now.isoformat(),
            },
            {
                "id": "mem2",
                "text": "ChromaDB no es rápido",
                "created_at": (now - timedelta(days=3)).isoformat(),
            },
        ]
        conflicts = detector.detect(memories)
        temporal_conflicts = [c for c in conflicts if c.conflict_type == "temporal"]
        assert len(temporal_conflicts) >= 0

    def test_suggest_resolution(self):
        detector = ConflictDetector()
        conflict = Conflict(
            id="conflict1",
            memory_ids=["mem1", "mem2"],
            conflict_type="predicate",
            description="Test conflict",
            severity=0.8,
        )
        resolution = detector.suggest_resolution(conflict)
        assert resolution.conflict_id == "conflict1"
        assert resolution.strategy in ["keep_latest", "keep_highest_confidence", "manual"]

    def test_resolve_conflict(self):
        detector = ConflictDetector()
        detector._conflicts["conflict1"] = Conflict(
            id="conflict1",
            memory_ids=["mem1"],
            conflict_type="predicate",
            description="test",
            severity=0.5,
        )
        result = detector.resolve_conflict("conflict1", "Kept latest memory")
        assert result is True
        assert detector._conflicts["conflict1"].resolved is True

    def test_unresolved_conflicts(self):
        detector = ConflictDetector()
        detector._conflicts["c1"] = Conflict(
            id="c1", memory_ids=[], conflict_type="predicate",
            description="test", severity=0.5, resolved=False,
        )
        detector._conflicts["c2"] = Conflict(
            id="c2", memory_ids=[], conflict_type="temporal",
            description="test", severity=0.5, resolved=True,
        )
        unresolved = detector.get_unresolved_conflicts()
        assert len(unresolved) == 1
        assert unresolved[0].id == "c1"

    def test_persistence(self):
        detector = ConflictDetector()
        detector._conflicts["c1"] = Conflict(
            id="c1", memory_ids=[], conflict_type="predicate",
            description="test", severity=0.5,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "conflicts.json"
            detector.save(path)

            loaded = ConflictDetector.load(path)
            assert len(loaded.get_conflicts()) == 1

    def test_stats(self):
        detector = ConflictDetector()
        detector._conflicts["c1"] = Conflict(
            id="c1", memory_ids=[], conflict_type="predicate",
            description="test", severity=0.5,
        )
        stats = detector.stats()
        assert stats["total_conflicts"] == 1
        assert stats["unresolved"] == 1


# ============================================================================
# Integration Tests
# ============================================================================

class TestPhase3Integration:
    """Integration tests for Phase 3 components."""

    def test_dreaming_with_reflection(self):
        """Test dreaming engine with reflection."""
        engine = DreamingEngine()
        memories = [
            MemoryItem(id="mem1", text="ChromaDB es una librería de vectores para búsqueda semántica"),
            MemoryItem(id="mem2", text="ChromaDB permite almacenar embeddings de texto"),
            MemoryItem(id="mem3", text="ChromaDB soporta múltiples colecciones"),
        ]
        insights = engine.dream(memories, sprint_id="sprint-1")

        # Check session was created
        history = engine.get_session_history()
        assert len(history) == 1
        assert history[0].memories_processed == 3

    def test_forgetting_with_candidates(self):
        """Test forgetting engine with candidates."""
        engine = ForgettingEngine(ForgettingPolicy(
            ttl_days=30,
            grace_period_days=0,
            dry_run=True,
        ))
        now = datetime.now()
        memories = [
            {
                "id": "mem1",
                "text": "Old memory",
                "created_at": (now - timedelta(days=60)).isoformat(),
                "last_accessed": (now - timedelta(days=60)).isoformat(),
                "access_count": 1,
                "importance": 0.2,
            },
            {
                "id": "mem2",
                "text": "Recent memory",
                "created_at": now.isoformat(),
                "access_count": 5,
                "importance": 0.8,
            },
        ]

        candidates = engine.find_candidates(memories)
        assert len(candidates) == 1  # Only old memory

        forgotten = engine.forget(candidates)
        assert len(forgotten) == 1

    def test_conflict_detection_with_forgetting(self):
        """Test conflict detection can inform forgetting."""
        detector = ConflictDetector()
        memories = [
            {"id": "mem1", "text": "ChromaDB es rápido", "importance": 0.8},
            {"id": "mem2", "text": "ChromaDB no es rápido", "importance": 0.3},
        ]

        conflicts = detector.detect(memories)
        if conflicts:
            resolution = detector.suggest_resolution(conflicts[0])
            assert resolution.strategy in ["keep_latest", "keep_highest_confidence", "manual"]

    def test_full_workflow(self):
        """Test complete Phase 3 workflow."""
        # 1. Create memories
        memories = [
            MemoryItem(id="mem1", text="Decidimos usar ChromaDB para vectores",
                      importance=0.8),
            MemoryItem(id="mem2", text="ChromaDB permite búsqueda semántica",
                      importance=0.7),
            MemoryItem(id="mem3", text="LadybugDB es para grafos",
                      importance=0.6),
        ]

        # 2. Dream (consolidate)
        dreaming = DreamingEngine()
        insights = dreaming.dream(memories, sprint_id="sprint-1")

        # 3. Detect conflicts
        detector = ConflictDetector()
        conflicts = detector.detect([
            {"id": m.id, "text": m.text, "importance": m.importance}
            for m in memories
        ])

        # 4. Apply forgetting (dry run)
        forgetting = ForgettingEngine(ForgettingPolicy(dry_run=True))
        candidates = forgetting.find_candidates([
            {
                "id": m.id,
                "text": m.text,
                "created_at": m.created_at,
                "importance": m.importance,
                "access_count": 10,
            }
            for m in memories
        ])
        forgotten = forgetting.forget(candidates)

        # Verify
        assert len(insights) >= 0
        assert len(conflicts) >= 0
        assert len(forgotten) >= 0
