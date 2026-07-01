#!/usr/bin/env python3
"""evol_contradictions.py — Contradiction detection for Evol-DD.

Detects contradictory facts in the memory system:
- Same subject with different predicates
- Invalidated facts still referenced as active
- Temporal inconsistencies

Adopted from MemPalace's contradiction detection concept.

Usage:
    from evol_contradictions import ContradictionDetector
    detector = ContradictionDetector()
    contradictions = detector.detect()
    suggestions = detector.suggest_resolution(contradictions)
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))


class ContradictionDetector:
    """Detects contradictory facts in the memory system."""
    
    def __init__(self, project_dir: str = None):
        """Initialize ContradictionDetector.
        
        Args:
            project_dir: Project directory (default: current)
        """
        self.project_dir = project_dir or os.getcwd()
        self._memory_dir = Path(os.environ.get('EVOL_MEMORY_DIR', 
                                               os.path.expanduser('~/.evol/memory')))
    
    def detect(self) -> List[Dict]:
        """Detect contradictions in the memory system.
        
        Returns:
            List of contradiction dicts:
            - type: 'temporal', 'predicate', 'invalidated'
            - severity: 'warning', 'error'
            - details: specific description
            - items: list of conflicting items
        """
        contradictions = []
        
        # 1. Check for invalidated facts still referenced as active
        contradictions.extend(self._check_invalidated_facts())
        
        # 2. Check for predicate contradictions
        contradictions.extend(self._check_predicate_contradictions())
        
        # 3. Check for temporal inconsistencies
        contradictions.extend(self._check_temporal_inconsistencies())
        
        return contradictions
    
    def _check_invalidated_facts(self) -> List[Dict]:
        """Check for invalidated facts still referenced as active."""
        contradictions = []
        
        invalidations_file = self._memory_dir / 'invalidations.json'
        if not invalidations_file.exists():
            return contradictions
        
        with open(invalidations_file) as f:
            invalidations = json.load(f)
        
        # Check if any invalidated facts are still in the index
        idx_file = self._memory_dir / 'local_index.json'
        if not idx_file.exists():
            return contradictions
        
        with open(idx_file) as f:
            index = json.load(f)
        
        for item in index:
            item_id = item.get('id', '')
            content = item.get('text', '').lower()
            
            # Check if this item's fact was invalidated
            for rel_key, ended_date in invalidations.items():
                src, rel, tgt = rel_key.split('->', 2)
                if src.lower() in content or tgt.lower() in content:
                    contradictions.append({
                        'type': 'invalidated',
                        'severity': 'warning',
                        'details': f"Item '{item_id}' references fact '{rel_key}' which was invalidated on {ended_date}",
                        'items': [item_id, rel_key],
                        'suggestion': f"Consider updating or removing this item as the fact is no longer active"
                    })
        
        return contradictions
    
    def _check_predicate_contradictions(self) -> List[Dict]:
        """Check for predicate contradictions (same subject, different predicates)."""
        contradictions = []
        
        idx_file = self._memory_dir / 'local_index.json'
        if not idx_file.exists():
            return contradictions
        
        with open(idx_file) as f:
            index = json.load(f)
        
        # Group by project and tipo
        grouped = {}
        for item in index:
            meta = item.get('metadata', {})
            key = f"{meta.get('proyecto', 'unknown')}:{meta.get('tipo', 'unknown')}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)
        
        # Check for contradictions within each group
        for key, items in grouped.items():
            if len(items) < 2:
                continue
            
            # Check for explicit negation patterns
            for i, item1 in enumerate(items):
                text1 = item1.get('text', '').lower()
                for item2 in items[i+1:]:
                    text2 = item2.get('text', '').lower()
                    
                    # Check for negation patterns
                    if self._has_negation(text1, text2):
                        contradictions.append({
                            'type': 'predicate',
                            'severity': 'warning',
                            'details': f"Potential contradiction: '{item1.get('text', '')[:50]}...' vs '{item2.get('text', '')[:50]}...'",
                            'items': [item1.get('id', ''), item2.get('id', '')],
                            'suggestion': "Review these items for consistency"
                        })
        
        return contradictions
    
    def _check_temporal_inconsistencies(self) -> List[Dict]:
        """Check for temporal inconsistencies."""
        contradictions = []
        
        idx_file = self._memory_dir / 'local_index.json'
        if not idx_file.exists():
            return contradictions
        
        with open(idx_file) as f:
            index = json.load(f)
        
        # Check for items with conflicting dates
        dated_items = []
        for item in index:
            meta = item.get('metadata', {})
            fecha = meta.get('fecha')
            if fecha:
                dated_items.append((fecha, item))
        
        # Sort by date
        dated_items.sort(key=lambda x: x[0])
        
        # Check for items with same date but conflicting info
        date_groups = {}
        for fecha, item in dated_items:
            if fecha not in date_groups:
                date_groups[fecha] = []
            date_groups[fecha].append(item)
        
        for fecha, items in date_groups.items():
            if len(items) < 2:
                continue
            
            # Check for conflicting decisions on same date
            decisions = [i for i in items if i.get('metadata', {}).get('tipo') == 'decision']
            if len(decisions) > 1:
                contradictions.append({
                    'type': 'temporal',
                    'severity': 'info',
                    'details': f"Multiple decisions on {fecha}: {len(decisions)} items",
                    'items': [d.get('id', '') for d in decisions],
                    'suggestion': "Review if these decisions are consistent"
                })
        
        return contradictions
    
    def _has_negation(self, text1: str, text2: str) -> bool:
        """Check if two texts contain negated versions of each other.
        
        Only matches specific patterns that indicate actual contradictions,
        not just the presence of negation words.
        """
        # More specific contradiction patterns
        contradiction_patterns = [
            # Direct negation of the same concept
            (r'\bno\s+implementamos\b', r'\bimplementamos\b'),
            (r'\bno\s+usamos\b', r'\busamos\b'),
            (r'\bno\s+decidimos\b', r'\bdecidimos\b'),
            # Opposite states
            (r'\bno\s+está\s+completo\b', r'\bestá\s+completo\b'),
            (r'\bno\s+está\s+activa\b', r'\bestá\s+activa\b'),
            (r'\bno\s+funciona\b', r'\bfunciona\b'),
            # True/false, correct/incorrect
            (r'\bfalso\b', r'\bverdadero\b'),
            (r'\bincorrecto\b', r'\bcorrecto\b'),
        ]
        
        for pattern1, pattern2 in contradiction_patterns:
            # Check if text1 has negation and text2 has positive, or vice versa
            if re.search(pattern1, text1) and re.search(pattern2, text2):
                return True
            if re.search(pattern1, text2) and re.search(pattern2, text1):
                return True
        
        return False
    
    def suggest_resolution(self, contradictions: List[Dict]) -> List[Dict]:
        """Suggest resolution for contradictions.
        
        Args:
            contradictions: List of contradictions from detect()
        
        Returns:
            List of suggestions with priority
        """
        suggestions = []
        
        for i, contradiction in enumerate(contradictions):
            severity = contradiction.get('severity', 'info')
            contradiction_type = contradiction.get('type', 'unknown')
            
            # Generate suggestion based on type and severity
            if contradiction_type == 'invalidated':
                suggestions.append({
                    'priority': 'high' if severity == 'error' else 'medium',
                    'action': 'review_and_update',
                    'details': contradiction.get('details', ''),
                    'items': contradiction.get('items', []),
                    'recommendation': 'Update or remove the item referencing the invalidated fact'
                })
            elif contradiction_type == 'predicate':
                suggestions.append({
                    'priority': 'medium',
                    'action': 'verify_consistency',
                    'details': contradiction.get('details', ''),
                    'items': contradiction.get('items', []),
                    'recommendation': 'Verify which fact is correct and update accordingly'
                })
            elif contradiction_type == 'temporal':
                suggestions.append({
                    'priority': 'low',
                    'action': 'review_decisions',
                    'details': contradiction.get('details', ''),
                    'items': contradiction.get('items', []),
                    'recommendation': 'Review multiple decisions for consistency'
                })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
        
        return suggestions


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Contradiction Detection")
    parser.add_argument("--project-dir", default=os.getcwd(),
                        help="Project directory")
    parser.add_argument("--detect", action="store_true",
                        help="Detect contradictions")
    parser.add_argument("--suggest", action="store_true",
                        help="Suggest resolutions")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    
    args = parser.parse_args()
    detector = ContradictionDetector(args.project_dir)
    
    if args.detect or args.suggest:
        contradictions = detector.detect()
        
        if args.suggest:
            suggestions = detector.suggest_resolution(contradictions)
            if args.json:
                print(json.dumps(suggestions, indent=2))
            else:
                print(f"Found {len(contradictions)} contradictions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"\n{i}. [{suggestion['priority'].upper()}] {suggestion['action']}")
                    print(f"   {suggestion['details']}")
                    print(f"   Recommendation: {suggestion['recommendation']}")
        else:
            if args.json:
                print(json.dumps(contradictions, indent=2))
            else:
                print(f"Found {len(contradictions)} contradictions:")
                for i, c in enumerate(contradictions, 1):
                    print(f"\n{i}. [{c['severity'].upper()}] {c['type']}")
                    print(f"   {c['details']}")
                    print(f"   Suggestion: {c.get('suggestion', 'N/A')}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
