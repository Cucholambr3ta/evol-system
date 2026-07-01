#!/usr/bin/env python3
"""Tests for evol_memory_stack.py"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from evol_memory_stack import MemoryStack, _load_identity, _load_essential_story


def test_load_identity():
    """Identity loads from AGENT_MEMORY.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal AGENT_MEMORY.md
        agent_memory = Path(tmpdir) / "AGENT_MEMORY.md"
        agent_memory.write_text("# Agent Memory\n\nI am a test agent.\n")
        
        identity = _load_identity(tmpdir)
        assert "test agent" in identity.lower() or Path(tmpdir).name in identity


def test_load_identity_missing():
    """Identity works without AGENT_MEMORY.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        identity = _load_identity(tmpdir)
        assert Path(tmpdir).name in identity


def test_load_essential_story():
    """Essential story loads from EDMS."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['EVOL_MEMORY_DIR'] = tmpdir
        # Create minimal local index
        idx_file = Path(tmpdir) / 'local_index.json'
        items = [
            {
                "id": "test1",
                "text": "Test decision",
                "metadata": {
                    "proyecto": "test",
                    "tipo": "decision",
                    "importance": 0.8,
                    "path": "acuerdos/test.md"
                }
            }
        ]
        idx_file.write_text(json.dumps(items))
        
        story = _load_essential_story(tmpdir)
        assert "L1" in story
        assert "ESSENTIAL STORY" in story
        del os.environ['EVOL_MEMORY_DIR']


def test_memory_stack_wake_up():
    """MemoryStack wake-up returns L0 + L1."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['EVOL_MEMORY_DIR'] = tmpdir
        # Create minimal files
        agent_memory = Path(tmpdir) / "AGENT_MEMORY.md"
        agent_memory.write_text("# Agent Memory\n\nI am a test agent.\n")
        
        idx_file = Path(tmpdir) / 'local_index.json'
        items = [
            {
                "id": "test1",
                "text": "Test decision",
                "metadata": {
                    "proyecto": "test",
                    "tipo": "decision",
                    "importance": 0.8,
                    "path": "acuerdos/test.md"
                }
            }
        ]
        idx_file.write_text(json.dumps(items))
        
        stack = MemoryStack(tmpdir)
        wake_up = stack.wake_up()
        assert "L0" in wake_up or "Identity" in wake_up or "test agent" in wake_up.lower()
        assert "L1" in wake_up or "ESSENTIAL STORY" in wake_up
        del os.environ['EVOL_MEMORY_DIR']


def test_memory_stack_status():
    """MemoryStack status returns token counts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['EVOL_MEMORY_DIR'] = tmpdir
        stack = MemoryStack(tmpdir)
        status = stack.status()
        assert "identity_tokens" in status
        assert "story_tokens" in status
        assert "total_tokens" in status
        assert status["total_tokens"] >= 0
        del os.environ['EVOL_MEMORY_DIR']


if __name__ == "__main__":
    test_load_identity()
    test_load_identity_missing()
    test_load_essential_story()
    test_memory_stack_wake_up()
    test_memory_stack_status()
    print("All memory stack tests passed!")
