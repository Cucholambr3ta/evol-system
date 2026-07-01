"""Tests for EDMS Memory v2.0 Phase 4 - Portability and Ecosystem Components."""

import os
import tempfile
import pytest
from pathlib import Path

# Add scripts dir to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evol_memory_v2.agent_file import AgentFile, AgentMemorySnapshot
from evol_memory_v2.relational import RelationalIntelligence, RelationshipScore
from evol_memory_v2.api import MemoryAPI, APIConfig
from evol_memory_v2.migrate import MigrationTool, MigrationResult


# ============================================================================
# Agent File Tests
# ============================================================================

class TestAgentFile:
    """Tests for AgentFile."""

    def test_create_snapshot(self):
        agent_file = AgentFile()
        snapshot = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent",
            memories=[{"id": "mem1", "text": "test"}],
            entities=[{"name": "ChromaDB", "type": "technology"}],
        )
        assert snapshot.agent_id == "evol-builder"
        assert snapshot.agent_name == "Builder Agent"
        assert len(snapshot.memory_items) == 1
        assert len(snapshot.entities) == 1
        assert snapshot.checksum  # Should have checksum

    def test_verify_integrity(self):
        agent_file = AgentFile()
        snapshot = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent",
        )
        verification = snapshot.verify_integrity()
        assert verification["is_valid"] is True

    def test_save_and_load(self):
        agent_file = AgentFile()
        snapshot = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent",
            memories=[{"id": "mem1", "text": "test"}],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "agent.json"
            agent_file.save(snapshot, path)

            loaded = agent_file.load(path)
            assert loaded.agent_id == "evol-builder"
            assert len(loaded.memory_items) == 1

    def test_load_invalid_checksum(self):
        agent_file = AgentFile()
        snapshot = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "agent.json"
            agent_file.save(snapshot, path)

            # Tamper with file
            content = path.read_text()
            content = content.replace('"agent_name": "Builder Agent"', '"agent_name": "Tampered"')
            path.write_text(content)

            with pytest.raises(ValueError, match="Checksum mismatch"):
                agent_file.load(path)

    def test_merge_snapshots(self):
        agent_file = AgentFile()

        snapshot1 = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent",
            memories=[{"id": "mem1", "text": "test1"}],
        )

        snapshot2 = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent v2",
            memories=[{"id": "mem2", "text": "test2"}],
        )

        merged = agent_file.merge(snapshot1, snapshot2)
        assert merged.agent_id == "evol-builder"
        assert len(merged.memory_items) == 2

    def test_diff_snapshots(self):
        agent_file = AgentFile()

        snapshot1 = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent",
            memories=[{"id": "mem1", "text": "test1"}],
        )

        snapshot2 = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent",
            memories=[
                {"id": "mem1", "text": "test1"},
                {"id": "mem2", "text": "test2"},
            ],
        )

        diff = agent_file.diff(snapshot1, snapshot2)
        assert diff["differences"]["memories"]["count_change"] == 1

    def test_stats(self):
        agent_file = AgentFile()
        snapshot = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent",
            memories=[{"id": "mem1", "text": "test"}],
            entities=[{"name": "ChromaDB", "type": "technology"}],
        )
        stats = agent_file.stats(snapshot)
        assert stats["counts"]["memories"] == 1
        assert stats["counts"]["entities"] == 1


# ============================================================================
# Relational Intelligence Tests
# ============================================================================

class TestRelationalIntelligence:
    """Tests for RelationalIntelligence."""

    def test_record_interaction(self):
        ri = RelationalIntelligence()
        ri.record_interaction("evol-builder", "evol-qa", "code_review")
        stats = ri.stats()
        assert stats["total_interactions"] == 1

    def test_get_relationship_scores(self):
        ri = RelationalIntelligence()
        ri.record_interaction("evol-builder", "evol-qa", "code_review")
        ri.record_interaction("evol-builder", "evol-sec", "security_audit")

        scores = ri.get_relationship_scores("evol-builder")
        assert len(scores) == 2

    def test_get_top_relationships(self):
        ri = RelationalIntelligence()
        ri.record_interaction("evol-builder", "evol-qa", "code_review")
        ri.record_interaction("evol-builder", "evol-sec", "security_audit")
        ri.record_interaction("evol-builder", "evol-doc", "documentation")

        top = ri.get_top_relationships("evol-builder", top_k=2)
        assert len(top) == 2

    def test_suggest_collaborators(self):
        ri = RelationalIntelligence()
        ri.record_interaction("evol-builder", "evol-qa", "code_review")
        ri.record_interaction("evol-builder", "evol-sec", "code_review")

        suggestions = ri.suggest_collaborators("evol-builder", "code_review")
        assert len(suggestions) == 2
        assert suggestions[0]["agent_id"] in ["evol-qa", "evol-sec"]

    def test_get_mutual_relationships(self):
        ri = RelationalIntelligence()
        ri.record_interaction("evol-builder", "evol-qa", "code_review")
        ri.record_interaction("evol-qa", "evol-builder", "feedback")

        mutual = ri.get_mutual_relationships("evol-builder", "evol-qa")
        assert len(mutual) == 2

    def test_persistence(self):
        ri = RelationalIntelligence()
        ri.record_interaction("evol-builder", "evol-qa", "code_review")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "relational.json"
            ri.save(path)

            loaded = RelationalIntelligence.load(path)
            assert loaded.stats()["total_interactions"] == 1

    def test_stats(self):
        ri = RelationalIntelligence()
        ri.record_interaction("evol-builder", "evol-qa", "code_review")
        ri.record_interaction("evol-builder", "evol-sec", "security_audit")

        stats = ri.stats()
        assert stats["unique_pairs"] == 2
        assert stats["unique_entities"] == 3


# ============================================================================
# API Tests (Basic)
# ============================================================================

class TestMemoryAPI:
    """Tests for MemoryAPI."""

    def test_api_config(self):
        config = APIConfig(host="0.0.0.0", port=9999)
        assert config.host == "0.0.0.0"
        assert config.port == 9999

    def test_api_stats_stopped(self):
        # Create a mock memory store
        class MockStore:
            def stats(self):
                return {"test": True}

        api = MemoryAPI(MockStore())
        stats = api.stats()
        assert stats["status"] == "stopped"

    def test_api_endpoints(self):
        class MockStore:
            def stats(self):
                return {"test": True}

        api = MemoryAPI(MockStore())
        endpoints = api._get_endpoints()
        assert len(endpoints) == 9
        assert any("health" in e for e in endpoints)


# ============================================================================
# Migration Tool Tests
# ============================================================================

class TestMigrationTool:
    """Tests for MigrationTool."""

    def test_verify_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v1_path = Path(tmpdir) / "v1"
            v2_path = Path(tmpdir) / "v2"

            tool = MigrationTool(v1_store_path=v1_path, v2_store_path=v2_path)
            result = tool.verify()
            assert result["v1_count"] == 0
            assert result["v2_count"] == 0

    def test_migrate_dry_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v1_path = Path(tmpdir) / "v1"
            v2_path = Path(tmpdir) / "v2"

            # Create v1 data
            v1_path.mkdir(parents=True, exist_ok=True)
            v1_index = v1_path / "local_index.json"
            v1_index.write_text(json.dumps({
                "mem1": {"text": "test memory", "metadata": {"tipo": "decision"}},
                "mem2": {"text": "another memory", "metadata": {"tipo": "leccion"}},
            }))

            tool = MigrationTool(v1_store_path=v1_path, v2_store_path=v2_path)
            result = tool.migrate(dry_run=True)

            assert result.items_migrated == 2
            assert not v2_path.exists()  # Should not create v2 in dry run

    def test_migrate_actual(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v1_path = Path(tmpdir) / "v1"
            v2_path = Path(tmpdir) / "v2"

            # Create v1 data
            v1_path.mkdir(parents=True, exist_ok=True)
            v1_index = v1_path / "local_index.json"
            v1_index.write_text(json.dumps({
                "mem1": {"text": "test memory", "metadata": {"tipo": "decision"}},
            }))

            tool = MigrationTool(v1_store_path=v1_path, v2_store_path=v2_path)
            result = tool.migrate(dry_run=False)

            assert result.success is True
            assert result.items_migrated == 1
            assert v2_path.exists()

    def test_list_snapshots(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v1_path = Path(tmpdir) / "v1"
            v2_path = Path(tmpdir) / "v2"

            # Create v1 data
            v1_path.mkdir(parents=True, exist_ok=True)
            v1_index = v1_path / "local_index.json"
            v1_index.write_text(json.dumps({
                "mem1": {"text": "test memory"},
            }))

            tool = MigrationTool(v1_store_path=v1_path, v2_store_path=v2_path)
            tool.migrate(dry_run=False)

            snapshots = tool.list_snapshots()
            assert len(snapshots) == 1

    def test_rollback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v1_path = Path(tmpdir) / "v1"
            v2_path = Path(tmpdir) / "v2"

            # Create v1 data
            v1_path.mkdir(parents=True, exist_ok=True)
            v1_index = v1_path / "local_index.json"
            v1_index.write_text(json.dumps({
                "mem1": {"text": "test memory"},
            }))

            tool = MigrationTool(v1_store_path=v1_path, v2_store_path=v2_path)
            result = tool.migrate(dry_run=False)
            snapshot_id = result.snapshot_id

            # Rollback
            rollback_result = tool.rollback(snapshot_id)
            assert rollback_result.success is True

    def test_stats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            v1_path = Path(tmpdir) / "v1"
            v2_path = Path(tmpdir) / "v2"

            tool = MigrationTool(v1_store_path=v1_path, v2_store_path=v2_path)
            stats = tool.stats()
            assert "v1_path" in stats
            assert "v2_path" in stats
            assert "verification" in stats


# ============================================================================
# Integration Tests
# ============================================================================

class TestPhase4Integration:
    """Integration tests for Phase 4 components."""

    def test_agent_file_with_relational(self):
        """Test Agent File with Relational Intelligence."""
        # Create agent file
        agent_file = AgentFile()
        snapshot = agent_file.create_snapshot(
            agent_id="evol-builder",
            agent_name="Builder Agent",
            memories=[
                {"id": "mem1", "text": "Decidimos usar ChromaDB"},
                {"id": "mem2", "text": "LadybugDB para grafos"},
            ],
            entities=[
                {"name": "ChromaDB", "type": "technology"},
                {"name": "LadybugDB", "type": "technology"},
            ],
        )

        # Add relational data
        ri = RelationalIntelligence()
        ri.record_interaction("evol-builder", "evol-qa", "code_review")
        ri.record_interaction("evol-builder", "evol-sec", "security_audit")

        # Save both
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_path = Path(tmpdir) / "agent.json"
            relational_path = Path(tmpdir) / "relational.json"

            agent_file.save(snapshot, agent_path)
            ri.save(relational_path)

            # Load and verify
            loaded_snapshot = agent_file.load(agent_path)
            loaded_ri = RelationalIntelligence.load(relational_path)

            assert loaded_snapshot.agent_id == "evol-builder"
            assert loaded_ri.stats()["total_interactions"] == 2

    def test_migration_workflow(self):
        """Test complete migration workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            v1_path = Path(tmpdir) / "v1"
            v2_path = Path(tmpdir) / "v2"

            # Create v1 data
            v1_path.mkdir(parents=True, exist_ok=True)
            v1_index = v1_path / "local_index.json"
            v1_index.write_text(json.dumps({
                "mem1": {"text": "Decidimos usar ChromaDB", "metadata": {"tipo": "decision"}},
                "mem2": {"text": "LadybugDB para grafos", "metadata": {"tipo": "leccion"}},
            }))

            # Migrate
            tool = MigrationTool(v1_store_path=v1_path, v2_store_path=v2_path)
            result = tool.migrate(dry_run=False)

            assert result.success is True
            assert result.items_migrated == 2

            # Verify
            verification = tool.verify()
            assert verification["is_complete"] is True

            # Check snapshots
            snapshots = tool.list_snapshots()
            assert len(snapshots) == 1


# Need json for migration tests
import json
