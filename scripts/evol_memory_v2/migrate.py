"""
Migration tooling for EDMS Memory v2.0.

Migrates data from EDMS v1 to v2 with checksums and dry-run mode.

Part of EDMS Memory v2.0 Phase 4 - Portability and Ecosystem.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class MigrationSnapshot:
    """Snapshot of data before migration."""
    id: str
    created_at: str
    source_version: str
    target_version: str
    items_count: int
    checksum: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MigrationResult:
    """Result of a migration operation."""
    success: bool
    items_migrated: int
    items_skipped: int
    errors: list[str]
    duration_ms: float
    snapshot_id: str | None = None


class MigrationTool:
    """
    Migration tool for EDMS v1 to v2.

    Provides safe migration with checksums, dry-run mode, and rollback.

    Usage:
        tool = MigrationTool()

        # Dry run first
        result = tool.migrate(dry_run=True)
        print(f"Would migrate {result.items_migrated} items")

        # Actual migration
        result = tool.migrate(dry_run=False)
        print(f"Migrated {result.items_migrated} items")

        # Rollback if needed
        tool.rollback(snapshot_id="...")
    """

    def __init__(
        self,
        v1_store_path: str | Path | None = None,
        v2_store_path: str | Path | None = None,
    ):
        self._v1_path = Path(v1_store_path) if v1_store_path else Path.home() / ".evol" / "memory"
        self._v2_path = Path(v2_store_path) if v2_store_path else Path.home() / ".evol" / "memory_v2"

        # Snapshot storage (created lazily)
        self._snapshots_path = self._v2_path / "snapshots"

    def migrate(
        self,
        dry_run: bool = False,
        overwrite: bool = False,
    ) -> MigrationResult:
        """
        Migrate data from v1 to v2.

        Args:
            dry_run: If True, don't actually write data
            overwrite: If True, overwrite existing v2 data

        Returns:
            MigrationResult with details
        """
        start_time = datetime.now()
        errors: list[str] = []
        items_migrated = 0
        items_skipped = 0

        # Load v1 data
        v1_data = self._load_v1_data()
        if not v1_data:
            return MigrationResult(
                success=True,
                items_migrated=0,
                items_skipped=0,
                errors=["No v1 data found"],
                duration_ms=0,
            )

        # Create snapshot
        snapshot_id = None
        if not dry_run:
            snapshot_id = self._create_snapshot(v1_data)

        # Migrate each item
        for item_id, item_data in v1_data.items():
            try:
                # Check if item already exists in v2
                if not overwrite and self._item_exists_in_v2(item_id):
                    items_skipped += 1
                    continue

                # Transform v1 item to v2 format
                v2_item = self._transform_v1_to_v2(item_id, item_data)

                # Write to v2 (if not dry run)
                if not dry_run:
                    self._write_v2_item(item_id, v2_item)

                items_migrated += 1

            except Exception as e:
                errors.append(f"Error migrating {item_id}: {str(e)}")

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds() * 1000

        return MigrationResult(
            success=len(errors) == 0,
            items_migrated=items_migrated,
            items_skipped=items_skipped,
            errors=errors,
            duration_ms=duration,
            snapshot_id=snapshot_id,
        )

    def rollback(self, snapshot_id: str) -> MigrationResult:
        """
        Rollback to a snapshot.

        Args:
            snapshot_id: ID of snapshot to rollback to

        Returns:
            MigrationResult with details
        """
        start_time = datetime.now()
        errors: list[str] = []

        # Load snapshot
        snapshot_path = self._snapshots_path / f"{snapshot_id}.json"
        if not snapshot_path.exists():
            return MigrationResult(
                success=False,
                items_migrated=0,
                items_skipped=0,
                errors=[f"Snapshot not found: {snapshot_id}"],
                duration_ms=0,
            )

        snapshot_data = json.loads(snapshot_path.read_text())

        # Restore v1 data from snapshot
        items_migrated = 0
        for item_id, item_data in snapshot_data.get("items", {}).items():
            try:
                self._write_v1_item(item_id, item_data)
                items_migrated += 1
            except Exception as e:
                errors.append(f"Error restoring {item_id}: {str(e)}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return MigrationResult(
            success=len(errors) == 0,
            items_migrated=items_migrated,
            items_skipped=0,
            errors=errors,
            duration_ms=duration,
            snapshot_id=snapshot_id,
        )

    def verify(self) -> dict[str, Any]:
        """
        Verify migration integrity.

        Returns:
            Dict with verification results
        """
        v1_data = self._load_v1_data()
        v2_data = self._load_v2_data()

        v1_count = len(v1_data) if v1_data else 0
        v2_count = len(v2_data) if v2_data else 0

        # Check for missing items
        missing_in_v2 = []
        if v1_data:
            for item_id in v1_data:
                if not self._item_exists_in_v2(item_id):
                    missing_in_v2.append(item_id)

        # Check for extra items in v2
        extra_in_v2 = []
        if v2_data and v1_data:
            for item_id in v2_data:
                if item_id not in v1_data:
                    extra_in_v2.append(item_id)

        return {
            "v1_count": v1_count,
            "v2_count": v2_count,
            "missing_in_v2": missing_in_v2,
            "extra_in_v2": extra_in_v2,
            "is_complete": len(missing_in_v2) == 0,
            "is_identical": v1_count == v2_count and len(extra_in_v2) == 0,
        }

    def _load_v1_data(self) -> dict[str, Any]:
        """Load all data from v1 store."""
        local_index_path = self._v1_path / "local_index.json"
        if not local_index_path.exists():
            return {}

        try:
            return json.loads(local_index_path.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _load_v2_data(self) -> dict[str, Any]:
        """Load all data from v2 store."""
        v2_index_path = self._v2_path / "local_index.json"
        if not v2_index_path.exists():
            return {}

        try:
            return json.loads(v2_index_path.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _item_exists_in_v2(self, item_id: str) -> bool:
        """Check if item exists in v2 store."""
        v2_data = self._load_v2_data()
        return item_id in v2_data

    def _transform_v1_to_v2(self, item_id: str, v1_item: dict[str, Any]) -> dict[str, Any]:
        """Transform v1 item format to v2 format."""
        # v2 adds content_hash and importance
        text = v1_item.get("text", "")
        content_hash = hashlib.sha256(text.encode()).hexdigest()[:16]

        return {
            "id": item_id,
            "text": text,
            "metadata": v1_item.get("metadata", {}),
            "content_hash": content_hash,
            "importance": v1_item.get("importance", 0.5),
            "created_at": v1_item.get("created_at", datetime.now().isoformat()),
            "migrated_from_v1": True,
            "migration_timestamp": datetime.now().isoformat(),
        }

    def _write_v2_item(self, item_id: str, item_data: dict[str, Any]) -> None:
        """Write item to v2 store."""
        # Only create directory when actually writing
        self._v2_path.mkdir(parents=True, exist_ok=True)
        v2_index_path = self._v2_path / "local_index.json"

        # Load existing v2 data
        v2_data = self._load_v2_data()

        # Add new item
        v2_data[item_id] = item_data

        # Write back
        v2_index_path.write_text(json.dumps(v2_data, ensure_ascii=False, indent=2))

    def _write_v1_item(self, item_id: str, item_data: dict[str, Any]) -> None:
        """Write item to v1 store (for rollback)."""
        self._v1_path.mkdir(parents=True, exist_ok=True)
        v1_index_path = self._v1_path / "local_index.json"

        # Load existing v1 data
        v1_data = self._load_v1_data()

        # Add item
        v1_data[item_id] = item_data

        # Write back
        v1_index_path.write_text(json.dumps(v1_data, ensure_ascii=False, indent=2))

    def _create_snapshot(self, data: dict[str, Any]) -> str:
        """Create snapshot of current data."""
        self._snapshots_path.mkdir(parents=True, exist_ok=True)

        snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        checksum = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()

        snapshot = MigrationSnapshot(
            id=snapshot_id,
            created_at=datetime.now().isoformat(),
            source_version="1.0.0",
            target_version="2.0.0",
            items_count=len(data),
            checksum=checksum,
        )

        # Save snapshot
        snapshot_data = {
            "id": snapshot.id,
            "created_at": snapshot.created_at,
            "source_version": snapshot.source_version,
            "target_version": snapshot.target_version,
            "items_count": snapshot.items_count,
            "checksum": snapshot.checksum,
            "items": data,
        }

        snapshot_path = self._snapshots_path / f"{snapshot_id}.json"
        snapshot_path.write_text(json.dumps(snapshot_data, ensure_ascii=False, indent=2))

        return snapshot_id

    def list_snapshots(self) -> list[dict[str, Any]]:
        """List all available snapshots."""
        snapshots = []

        for snapshot_file in self._snapshots_path.glob("snapshot_*.json"):
            try:
                data = json.loads(snapshot_file.read_text())
                snapshots.append({
                    "id": data["id"],
                    "created_at": data["created_at"],
                    "items_count": data["items_count"],
                    "checksum": data["checksum"],
                })
            except (json.JSONDecodeError, KeyError):
                continue

        return sorted(snapshots, key=lambda s: s["created_at"], reverse=True)

    def stats(self) -> dict[str, Any]:
        """Get migration tool statistics."""
        snapshots = self.list_snapshots()
        verification = self.verify()

        return {
            "v1_path": str(self._v1_path),
            "v2_path": str(self._v2_path),
            "snapshots_count": len(snapshots),
            "verification": verification,
        }
