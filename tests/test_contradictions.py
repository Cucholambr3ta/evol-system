#!/usr/bin/env python3
"""Tests for evol_contradictions.py"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from evol_contradictions import ContradictionDetector


def test_detect_no_contradictions():
    """No contradictions in clean memory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['EVOL_MEMORY_DIR'] = tmpdir
        # Create empty index
        idx_file = Path(tmpdir) / 'local_index.json'
        idx_file.write_text("[]")
        
        detector = ContradictionDetector(tmpdir)
        contradictions = detector.detect()
        # Should have no contradictions (or only temporal from multiple decisions)
        assert len(contradictions) == 0
        del os.environ['EVOL_MEMORY_DIR']


def test_detect_invalidated_fact():
    """Detect invalidated fact still referenced."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['EVOL_MEMORY_DIR'] = tmpdir
        
        # Create invalidations
        invalidations_file = Path(tmpdir) / 'invalidations.json'
        invalidations_file.write_text(json.dumps({
            "test->USES->old_tech": "2026-06-01"
        }))
        
        # Create index with item referencing invalidated fact
        idx_file = Path(tmpdir) / 'local_index.json'
        idx_file.write_text(json.dumps([
            {
                "id": "item1",
                "text": "We use old_tech for this",
                "metadata": {"proyecto": "test", "tipo": "decision"}
            }
        ]))
        
        detector = ContradictionDetector(tmpdir)
        contradictions = detector.detect()
        invalidated = [c for c in contradictions if c['type'] == 'invalidated']
        assert len(invalidated) >= 1
        del os.environ['EVOL_MEMORY_DIR']


def test_detect_predicate_contradiction():
    """Detect predicate contradiction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['EVOL_MEMORY_DIR'] = tmpdir
        
        # Create index with contradictory items
        idx_file = Path(tmpdir) / 'local_index.json'
        idx_file.write_text(json.dumps([
            {
                "id": "item1",
                "text": "No implementamos la feature X",
                "metadata": {"proyecto": "test", "tipo": "decision"}
            },
            {
                "id": "item2",
                "text": "Implementamos la feature X",
                "metadata": {"proyecto": "test", "tipo": "decision"}
            }
        ]))
        
        detector = ContradictionDetector(tmpdir)
        contradictions = detector.detect()
        predicate = [c for c in contradictions if c['type'] == 'predicate']
        assert len(predicate) >= 1
        del os.environ['EVOL_MEMORY_DIR']


def test_suggest_resolution():
    """Suggest resolution for contradictions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['EVOL_MEMORY_DIR'] = tmpdir
        
        # Create invalidations
        invalidations_file = Path(tmpdir) / 'invalidations.json'
        invalidations_file.write_text(json.dumps({
            "test->USES->old_tech": "2026-06-01"
        }))
        
        # Create index with item referencing invalidated fact
        idx_file = Path(tmpdir) / 'local_index.json'
        idx_file.write_text(json.dumps([
            {
                "id": "item1",
                "text": "We use old_tech for this",
                "metadata": {"proyecto": "test", "tipo": "decision"}
            }
        ]))
        
        detector = ContradictionDetector(tmpdir)
        contradictions = detector.detect()
        suggestions = detector.suggest_resolution(contradictions)
        assert len(suggestions) >= 1
        assert 'priority' in suggestions[0]
        assert 'action' in suggestions[0]
        del os.environ['EVOL_MEMORY_DIR']


if __name__ == "__main__":
    test_detect_no_contradictions()
    test_detect_invalidated_fact()
    test_detect_predicate_contradiction()
    test_suggest_resolution()
    print("All contradiction detection tests passed!")
