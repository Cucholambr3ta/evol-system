"""
Dreaming engine for EDMS Memory v2.0.

Consolidates memories during system idle periods, aligned with sprint cycles.
Implements batch processing with progress tracking.

Part of EDMS Memory v2.0 Phase 3 - Consolidation and Dreaming.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .reflection import Insight, MemoryItem, ReflectionEngine


@dataclass
class DreamSession:
    """A single dreaming session."""
    id: str
    started_at: str
    ended_at: str = ""
    status: str = "running"  # running, completed, failed
    memories_processed: int = 0
    insights_generated: int = 0
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DreamConfig:
    """Configuration for dreaming sessions."""
    max_memories_per_batch: int = 100
    max_duration_seconds: float = 300.0  # 5 minutes
    min_cluster_size: int = 3
    min_confidence: float = 0.6
    enable_patterns: bool = True
    enable_trends: bool = True
    enable_evolutions: bool = True
    enable_cross_cluster: bool = True


class DreamingEngine:
    """
    Sprint-aware dreaming engine.

    Consolidates memories during system idle periods, aligned with
    sprint cycles. Processes memories in batches with progress tracking.

    Usage:
        engine = DreamingEngine()
        session = engine.start_dream_session()
        # ... process memories ...
        session = engine.end_dream_session()
    """

    def __init__(self, config: DreamConfig | None = None):
        self.config = config or DreamConfig()

        # Reflection engine
        self._reflection = ReflectionEngine(
            min_cluster_size=self.config.min_cluster_size,
            min_confidence=self.config.min_confidence,
        )

        # Session history
        self._sessions: dict[str, DreamSession] = {}

        # Current session
        self._current_session: DreamSession | None = None

        # Insight storage
        self._insights: dict[str, Insight] = {}

        # Session counter for unique IDs
        self._session_counter: int = 0

    def start_dream_session(self) -> DreamSession:
        """
        Start a new dreaming session.

        Returns:
            DreamSession with session ID
        """
        self._session_counter += 1
        session_id = f"dream_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self._session_counter}"

        session = DreamSession(
            id=session_id,
            started_at=datetime.now().isoformat(),
        )

        self._current_session = session
        self._sessions[session_id] = session

        return session

    def end_dream_session(self) -> DreamSession | None:
        """
        End the current dreaming session.

        Returns:
            Completed DreamSession or None
        """
        if not self._current_session:
            return None

        session = self._current_session
        session.ended_at = datetime.now().isoformat()
        session.status = "completed"

        # Calculate duration
        start = datetime.fromisoformat(session.started_at)
        end = datetime.fromisoformat(session.ended_at)
        session.duration_ms = (end - start).total_seconds() * 1000

        self._current_session = None

        return session

    def dream(
        self,
        memories: list[MemoryItem],
        sprint_id: str | None = None,
    ) -> list[Insight]:
        """
        Process memories and generate insights.

        Args:
            memories: List of MemoryItem to process
            sprint_id: Optional sprint identifier

        Returns:
            List of generated Insight objects
        """
        # Start a new session if none active
        if not self._current_session:
            self.start_dream_session()

        session = self._current_session
        session.memories_processed = len(memories)
        if sprint_id:
            session.metadata["sprint_id"] = sprint_id

        # Process in batches
        all_insights: list[Insight] = []
        batch_size = self.config.max_memories_per_batch

        for i in range(0, len(memories), batch_size):
            batch = memories[i:i + batch_size]

            # Run reflection on batch
            insights = self._reflection.reflect(batch)
            all_insights.extend(insights)

            # Store insights
            for insight in insights:
                self._insights[insight.id] = insight

        session.insights_generated = len(all_insights)

        # End session
        self.end_dream_session()

        return all_insights

    def get_insights(
        self,
        insight_type: str | None = None,
        min_confidence: float | None = None,
    ) -> list[Insight]:
        """
        Get insights with optional filtering.

        Args:
            insight_type: Filter by type (pattern, trend, evolution, etc.)
            min_confidence: Filter by minimum confidence

        Returns:
            List of Insight objects
        """
        insights = list(self._insights.values())

        if insight_type:
            insights = [i for i in insights if i.insight_type == insight_type]

        if min_confidence is not None:
            insights = [i for i in insights if i.confidence >= min_confidence]

        return insights

    def get_session_history(self) -> list[DreamSession]:
        """Get history of all dreaming sessions."""
        return list(self._sessions.values())

    def get_latest_session(self) -> DreamSession | None:
        """Get the most recent dreaming session."""
        if not self._sessions:
            return None

        return max(self._sessions.values(), key=lambda s: s.started_at)

    def stats(self) -> dict[str, Any]:
        """Get dreaming engine statistics."""
        sessions = list(self._sessions.values())
        insights = list(self._insights.values())

        total_memories = sum(s.memories_processed for s in sessions)
        total_insights = sum(s.insights_generated for s in sessions)

        return {
            "total_sessions": len(sessions),
            "total_memories_processed": total_memories,
            "total_insights_generated": total_insights,
            "avg_memories_per_session": round(total_memories / max(len(sessions), 1), 1),
            "avg_insights_per_session": round(total_insights / max(len(sessions), 1), 1),
            "insight_types": {
                t: len([i for i in insights if i.insight_type == t])
                for t in set(i.insight_type for i in insights)
            } if insights else {},
        }

    # -----------------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Save dreaming state to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "sessions": [
                {
                    "id": s.id,
                    "started_at": s.started_at,
                    "ended_at": s.ended_at,
                    "status": s.status,
                    "memories_processed": s.memories_processed,
                    "insights_generated": s.insights_generated,
                    "duration_ms": s.duration_ms,
                    "metadata": s.metadata,
                }
                for s in self._sessions.values()
            ],
            "insights": [
                {
                    "id": i.id,
                    "summary": i.summary,
                    "source_ids": i.source_ids,
                    "insight_type": i.insight_type,
                    "confidence": i.confidence,
                    "created_at": i.created_at,
                    "metadata": i.metadata,
                }
                for i in self._insights.values()
            ],
        }

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> DreamingEngine:
        """Load dreaming state from JSON file."""
        path = Path(path)
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())
        engine = cls()

        # Load sessions
        for session_data in data.get("sessions", []):
            session = DreamSession(
                id=session_data["id"],
                started_at=session_data["started_at"],
                ended_at=session_data.get("ended_at", ""),
                status=session_data.get("status", "completed"),
                memories_processed=session_data.get("memories_processed", 0),
                insights_generated=session_data.get("insights_generated", 0),
                duration_ms=session_data.get("duration_ms", 0.0),
                metadata=session_data.get("metadata", {}),
            )
            engine._sessions[session.id] = session

        # Load insights
        for insight_data in data.get("insights", []):
            insight = Insight(
                id=insight_data["id"],
                summary=insight_data["summary"],
                source_ids=insight_data.get("source_ids", []),
                insight_type=insight_data.get("insight_type", "pattern"),
                confidence=insight_data.get("confidence", 0.5),
                created_at=insight_data.get("created_at", ""),
                metadata=insight_data.get("metadata", {}),
            )
            engine._insights[insight.id] = insight

        return engine
