#!/usr/bin/env python3
"""minimal.py — level state + `minimal:` marker scan for the evol-minimal skill.

Stdlib only (the skill eats its own dog food). Two jobs:

  level [LEVEL]   get or set the enforcement level (.evol/.minimal-level)
  debt [PATH]     scan for `minimal:` markers and emit ledger-ready JSON

Levels: lite | full | ultra | off. Default: full.
"""

import argparse
import json
import re
import sys
from pathlib import Path

LEVELS = ("lite", "full", "ultra", "off")
DEFAULT_LEVEL = "full"
STATE = Path(".evol/.minimal-level")
# Only count markers in a comment (#, //, --, ;, <!--), not prose mentions.
MARKER = re.compile(r"(?:#|//|--|;|<!--)\s*minimal:\s*(.+?)\s*(?:-->)?$")
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist", ".pytest_cache"}


def get_level() -> str:
    if STATE.exists():
        lvl = STATE.read_text().strip()
        if lvl in LEVELS:
            return lvl
    return DEFAULT_LEVEL


def set_level(level: str) -> str:
    if level not in LEVELS:
        raise SystemExit(f"invalid level '{level}'; expected one of {', '.join(LEVELS)}")
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(level)
    return level


def scan_markers(root: Path) -> list[dict]:
    """Find `minimal:` markers; return ledger-ready entries."""
    out: list[dict] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(p in SKIP_DIRS for p in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            m = MARKER.search(line)
            if m:
                out.append({
                    "file": str(path),
                    "line": n,
                    "note": m.group(1).strip(),
                    "kind": "over-engineering",
                })
    return out


def main() -> None:
    ap = argparse.ArgumentParser(prog="minimal")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("level", help="get/set enforcement level")
    p.add_argument("level", nargs="?", help=f"one of {', '.join(LEVELS)}")

    p = sub.add_parser("debt", help="scan `minimal:` markers as ledger JSON")
    p.add_argument("path", nargs="?", default=".", help="root to scan")

    args = ap.parse_args()
    if args.cmd == "level":
        print(set_level(args.level) if args.level else get_level())
    elif args.cmd == "debt":
        entries = scan_markers(Path(args.path))
        json.dump({"markers": entries, "count": len(entries)}, sys.stdout,
                  ensure_ascii=False, indent=2)
        print()


if __name__ == "__main__":
    main()
