"""Tests for EDMS Memory v2.0 — thought capture (Gap 2)."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evol_memory_v2.store import VerbatimStore
from evol_memory_v2.thought import Thought, ThoughtStore


def _store():
    return VerbatimStore(tempfile.mkdtemp())


class TestThought:
    def test_to_text_includes_all_parts(self):
        t = Thought(
            chosen="Textual TUI",
            alternatives=["React+SSE", "Web PWA"],
            rejected_because="perdida de foco",
            context="UI final",
        )
        text = t.to_text()
        assert "Textual TUI" in text
        assert "React+SSE" in text
        assert "perdida de foco" in text
        assert "UI final" in text

    def test_to_text_minimal(self):
        t = Thought(chosen="X")
        assert t.to_text() == "Decision: X"

    def test_atom_metadata(self):
        t = Thought(chosen="X", alternatives=["Y"], rejected_because="z", context="c")
        meta = t.to_atom_metadata()
        assert meta["tipo"] == "thought"
        assert meta["chosen"] == "X"
        assert meta["alternatives"] == ["Y"]
        assert meta["rejected_because"] == "z"

    def test_created_at_autofilled(self):
        assert Thought(chosen="X").created_at != ""


class TestThoughtStore:
    def test_capture_and_list(self):
        ts = ThoughtStore(_store())
        ts.capture(Thought(chosen="ChromaDB", context="vector store"))
        items = ts.all()
        assert len(items) == 1
        assert items[0]["metadata"]["tipo"] == "thought"
        assert items[0]["metadata"]["chosen"] == "ChromaDB"

    def test_capture_is_idempotent(self):
        store = _store()
        ts = ThoughtStore(store)
        t = Thought(chosen="X", alternatives=["Y"], context="c")
        ts.capture(t)
        ts.capture(t)  # identical content -> dedup by hash
        assert len(ts.all()) == 1

    def test_for_context_filters(self):
        ts = ThoughtStore(_store())
        ts.capture(Thought(chosen="A", context="UI final EDMS"))
        ts.capture(Thought(chosen="B", context="vector store"))
        ui = ts.for_context("UI")
        assert len(ui) == 1
        assert ui[0]["metadata"]["chosen"] == "A"

    def test_for_context_case_insensitive(self):
        ts = ThoughtStore(_store())
        ts.capture(Thought(chosen="A", context="UI final"))
        assert len(ts.for_context("ui")) == 1

    def test_thoughts_excluded_from_other_type_queries(self):
        """A thought atom must carry tipo=thought, distinguishable from decisions."""
        store = _store()
        store.write("una decision normal", {"tipo": "decision"})
        ThoughtStore(store).capture(Thought(chosen="X"))
        thoughts = [
            it for it in store.list_items()
            if it.get("metadata", {}).get("tipo") == "thought"
        ]
        assert len(thoughts) == 1

    def test_empty_store(self):
        assert ThoughtStore(_store()).all() == []
