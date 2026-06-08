#!/usr/bin/env bash
# Post-commit hook: Incremental code graph index after git commit
# Triggered after successful git commit

PROJECT="${EVOL_PROJECT:-.}"

# Check if this is a git commit command
if [[ "$CLAUDE_BASH_COMMAND" == git\ commit* ]] || [[ "$CLAUDE_BASH_COMMAND" == git\ push* ]]; then
    if command -v python3 &>/dev/null; then
        # Run incremental code index in background
        python3 scripts/evol_code_indexer.py index "$PROJECT" 2>/dev/null &

        # Emit trace event
        python3 -c "
from evol_traces import emit_file_event
emit_file_event('$PROJECT', '.evol/code-graph', action='reindexed', agent='hook:post-commit')
" 2>/dev/null || true
    fi
fi
exit 0
