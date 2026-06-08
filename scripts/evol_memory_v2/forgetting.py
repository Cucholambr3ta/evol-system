"""
Automatic forgetting engine for EDMS Memory v2.0.

Implements controlled forgetting based on TTL, frequency, and relevance.
Includes grace period and dry-run mode for safety.

Part of EDMS Memory v2.0 Phase 3 - Consolidation and Dreaming.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass
class ForgettingPolicy:
    """Policy for forgetting memories."""
    # TTL in days (0 = never expire)
    ttl_days: int = 90

    # Minimum access count to keep
    min_access_count: int = 2

    # Minimum relevance score to keep (0-1)
    min_relevance: float = 0.3

    # Grace period in days after creation
    grace_period_days: int = 30

    # Maximum items to forget per run
    max_forget_per_run: int = 50

    # Enable dry-run mode (don't actually delete)
    dry_run: bool = False


@dataclass
class ForgettingCandidate:
    """A memory item candidate for forgetting."""
    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    last_accessed: str = ""
    access_count: int = 0
    relevance: float = 0.5
    reason: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_accessed:
            self.last_accessed = self.created_at


class ForgettingEngine:
    """
    Automatic forgetting engine.

    Implements controlled forgetting based on TTL, frequency, and relevance.
    Includes grace period and dry-run mode for safety.

    Usage:
        engine = ForgettingEngine()
        candidates = engine.find_candidates(memories)
        forgotten = engine.forget(candidates)
    """

    def __init__(self, policy: ForgettingPolicy | None = None):
        self.policy = policy or ForgettingPolicy()

        # Forgotten items history
        self._forgotten: list[dict[str, Any]] = []

        # Statistics
        self._stats = {
            "total_candidates": 0,
            "total_forgotten": 0,
            "total_skipped": 0,
        }

    def find_candidates(
        self,
        memories: list[dict[str, Any]],
    ) -> list[ForgettingCandidate]:
        """
        Find memory items that are candidates for forgetting.

        Args:
            memories: List of memory dicts with id, text, metadata, created_at, etc.

        Returns:
            List of ForgettingCandidate objects
        """
        candidates = []
        now = datetime.now()

        for mem in memories:
            candidate = self._evaluate_candidate(mem, now)
            if candidate:
                candidates.append(candidate)

        self._stats["total_candidates"] = len(candidates)

        return candidates

    def _evaluate_candidate(
        self,
        mem: dict[str, Any],
        now: datetime,
    ) -> ForgettingCandidate | None:
        """Evaluate if a memory is a forgetting candidate."""
        created_at = mem.get("created_at", "")
        last_accessed = mem.get("last_accessed", created_at)
        access_count = mem.get("access_count", 0)
        relevance = mem.get("importance", 0.5)

        # Parse dates
        try:
            created = datetime.fromisoformat(created_at) if created_at else now
            accessed = datetime.fromisoformat(last_accessed) if last_accessed else now
        except ValueError:
            return None

        # Check grace period
        age_days = (now - created).days
        if age_days < self.policy.grace_period_days:
            return None

        # Check TTL
        if self.policy.ttl_days > 0:
            days_since_access = (now - accessed).days
            if days_since_access > self.policy.ttl_days:
                return ForgettingCandidate(
                    id=mem.get("id", ""),
                    text=mem.get("text", ""),
                    metadata=mem.get("metadata", {}),
                    created_at=created_at,
                    last_accessed=last_accessed,
                    access_count=access_count,
                    relevance=relevance,
                    reason=f"Exceeded TTL ({days_since_access} days > {self.policy.ttl_days})",
                )

        # Check access count
        if access_count < self.policy.min_access_count:
            return ForgettingCandidate(
                id=mem.get("id", ""),
                text=mem.get("text", ""),
                metadata=mem.get("metadata", {}),
                created_at=created_at,
                last_accessed=last_accessed,
                access_count=access_count,
                relevance=relevance,
                reason=f"Low access count ({access_count} < {self.policy.min_access_count})",
            )

        # Check relevance
        if relevance < self.policy.min_relevance:
            return ForgettingCandidate(
                id=mem.get("id", ""),
                text=mem.get("text", ""),
                metadata=mem.get("metadata", {}),
                created_at=created_at,
                last_accessed=last_accessed,
                access_count=access_count,
                relevance=relevance,
                reason=f"Low relevance ({relevance:.2f} < {self.policy.min_relevance})",
            )

        return None

    def forget(
        self,
        candidates: list[ForgettingCandidate],
    ) -> list[ForgettingCandidate]:
        """
        Forget candidate items.

        Args:
            candidates: List of ForgettingCandidate to forget

        Returns:
            List of actually forgotten items
        """
        forgotten = []
        remaining = candidates[:self.policy.max_forget_per_run]

        for candidate in remaining:
            if self.policy.dry_run:
                # Dry run: just record what would be forgotten
                self._forgotten.append({
                    "id": candidate.id,
                    "reason": candidate.reason,
                    "dry_run": True,
                    "timestamp": datetime.now().isoformat(),
                })
                forgotten.append(candidate)
            else:
                # Actually forget
                self._forgotten.append({
                    "id": candidate.id,
                    "reason": candidate.reason,
                    "dry_run": False,
                    "timestamp": datetime.now().isoformat(),
                })
                forgotten.append(candidate)

        self._stats["total_forgotten"] += len(forgotten)
        self._stats["total_skipped"] += len(candidates) - len(forgotten)

        return forgotten

    def get_forgotten_history(self) -> list[dict[str, Any]]:
        """Get history of forgotten items."""
        return self._forgotten.copy()

    def stats(self) -> dict[str, Any]:
        """Get forgetting engine statistics."""
        return {
            **self._stats,
            "policy": {
                "ttl_days": self.policy.ttl_days,
                "min_access_count": self.policy.min_access_count,
                "min_relevance": self.policy.min_relevance,
                "grace_period_days": self.policy.grace_period_days,
                "max_forget_per_run": self.policy.max_forget_per_run,
                "dry_run": self.policy.dry_run,
            },
        }

    # -----------------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Save forgetting state to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "forgotten": self._forgotten,
            "stats": self._stats,
        }

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> ForgettingEngine:
        """Load forgetting state from JSON file."""
        path = Path(path)
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())
        engine = cls()

        engine._forgotten = data.get("forgotten", [])
        engine._stats = data.get("stats", {
            "total_candidates": 0,
            "total_forgotten": 0,
            "total_skipped": 0,
        })

        return engine
