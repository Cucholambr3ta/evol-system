#!/usr/bin/env python3
"""evol_memory_stack.py — Memory Stack (L0+L1) for Evol-DD.

Adopted from MemPalace's 4-layer memory stack philosophy:
- L0: Identity (~50-100 tokens) — who is this AI?
- L1: Essential Story (~500-800 tokens) — top moments from EDMS
- L2: On-Demand Recall — filtered retrieval (handled by evol_memory_store)
- L3: Deep Search — full semantic search (handled by evol_memory_store)

Usage:
    from evol_memory_stack import MemoryStack
    stack = MemoryStack()
    print(stack.wake_up())  # L0 + L1
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def _load_identity(project_dir: str = None) -> str:
    """Load L0: Identity layer.
    
    Reads AGENT_MEMORY.md and WORKING-CONTEXT.md to generate identity context.
    
    Args:
        project_dir: Project directory (default: current)
    
    Returns:
        Identity string (~50-100 tokens)
    """
    if not project_dir:
        project_dir = os.getcwd()
    
    project_name = Path(project_dir).name
    
    # Try to read AGENT_MEMORY.md
    agent_memory_path = Path(project_dir) / "AGENT_MEMORY.md"
    agent_memory_content = ""
    if agent_memory_path.exists():
        with open(agent_memory_path) as f:
            content = f.read()
            # Extract key info
            for line in content.split('\n'):
                if line.startswith('#'):
                    continue
                if line.strip() and not line.startswith('##'):
                    agent_memory_content += line.strip() + " "
    
    # Try to read WORKING-CONTEXT.md
    working_context_path = Path(project_dir) / "WORKING-CONTEXT.md"
    working_context_content = ""
    if working_context_path.exists():
        with open(working_context_path) as f:
            content = f.read()
            for line in content.split('\n'):
                if 'Branch:' in line or 'Fase:' in line or 'Version:' in line:
                    working_context_content += line.strip() + " "
    
    # Build identity
    identity = f"I am the Evol-DD assistant for {project_name}."
    if agent_memory_content:
        identity += f" {agent_memory_content[:200]}"
    if working_context_content:
        identity += f" Current state: {working_context_content}"
    
    return identity.strip()


def _load_essential_story(project_dir: str = None, max_items: int = 15,
                          max_chars: int = 3200) -> str:
    """Load L1: Essential Story layer.
    
    Auto-generates top moments from EDMS by importance.
    
    Args:
        project_dir: Project directory (default: current)
        max_items: Maximum items to include (default: 15)
        max_chars: Maximum characters (default: 3200)
    
    Returns:
        Essential story string (~500-800 tokens)
    """
    if not project_dir:
        project_dir = os.getcwd()
    
    # Import MemoryStore
    try:
        from evol_memory_store import MemoryStore
        store = MemoryStore()
    except Exception:
        return "[EDMS not available]"
    
    # Get items by importance
    idx_file = store.memory_dir / 'local_index.json'
    if not idx_file.exists():
        return "[No indexed items]"
    
    with open(idx_file) as f:
        index = json.load(f)
    
    # Sort by importance (descending)
    items = sorted(
        index,
        key=lambda x: x.get('metadata', {}).get('importance', 0.5),
        reverse=True
    )[:max_items]
    
    # Group by folder/path
    grouped = {}
    for item in items:
        path = item.get('metadata', {}).get('path', 'general')
        folder = Path(path).parent.name if '/' in path else 'general'
        if folder not in grouped:
            grouped[folder] = []
        
        # Extract summary from content
        content = item.get('content', '')
        if len(content) > 100:
            summary = content[:100] + "..."
        else:
            summary = content
        grouped[folder].append(summary)
    
    # Build story
    lines = ["## L1 — ESSENTIAL STORY", ""]
    for folder, summaries in grouped.items():
        lines.append(f"[{folder}]")
        for summary in summaries[:3]:  # Max 3 per folder
            lines.append(f"  - {summary}")
        lines.append("")
    
    story = "\n".join(lines)
    
    # Truncate if too long
    if len(story) > max_chars:
        story = story[:max_chars-3] + "..."
    
    return story


class MemoryStack:
    """Memory Stack (L0+L1) for Evol-DD.
    
    Adopted from MemPalace's 4-layer memory stack philosophy.
    Provides bounded startup context (~600-900 tokens).
    """
    
    def __init__(self, project_dir: str = None):
        """Initialize MemoryStack.
        
        Args:
            project_dir: Project directory (default: current)
        """
        self.project_dir = project_dir or os.getcwd()
        self._identity = None
        self._essential_story = None
    
    def wake_up(self) -> str:
        """Get L0 + L1 wake-up context (~600-900 tokens).
        
        Returns:
            Combined identity and essential story
        """
        return f"{self.get_identity()}\n\n{self.get_essential_story()}"
    
    def get_identity(self) -> str:
        """Get L0: Identity layer (~50-100 tokens).
        
        Returns:
            Identity string
        """
        if self._identity is None:
            self._identity = _load_identity(self.project_dir)
        return self._identity
    
    def get_essential_story(self) -> str:
        """Get L1: Essential Story layer (~500-800 tokens).
        
        Returns:
            Essential story string
        """
        if self._essential_story is None:
            self._essential_story = _load_essential_story(self.project_dir)
        return self._essential_story
    
    def status(self) -> dict:
        """Get memory stack status.
        
        Returns:
            Dict with status info
        """
        identity = self.get_identity()
        story = self.get_essential_story()
        
        return {
            "identity_tokens": len(identity.split()),
            "story_tokens": len(story.split()),
            "total_tokens": len((identity + story).split()),
            "project_dir": self.project_dir,
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Stack (L0+L1)")
    parser.add_argument("--project-dir", default=os.getcwd(),
                        help="Project directory")
    parser.add_argument("--wake-up", action="store_true",
                        help="Print full wake-up context (L0 + L1)")
    parser.add_argument("--identity", action="store_true",
                        help="Print L0 identity only")
    parser.add_argument("--story", action="store_true",
                        help="Print L1 essential story only")
    parser.add_argument("--status", action="store_true",
                        help="Print stack status")
    
    args = parser.parse_args()
    stack = MemoryStack(args.project_dir)
    
    if args.wake_up:
        print(stack.wake_up())
    elif args.identity:
        print(stack.get_identity())
    elif args.story:
        print(stack.get_essential_story())
    elif args.status:
        status = stack.status()
        print(json.dumps(status, indent=2))
    else:
        # Default: print wake-up
        print(stack.wake_up())
