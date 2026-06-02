#!/usr/bin/env bash
# PostToolUse hook: Re-index MemPalace (async)

if command -v mempalace >/dev/null 2>&1; then
    (mempalace index --wing evol-dd --path . 2>/dev/null || true) &
fi
exit 0