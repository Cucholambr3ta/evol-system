#!/usr/bin/env bash
# PreToolUse hook: Block config edits without justification

PROTECTED="evol.config.yml evol.profile.yml hooks.json"

for f in $PROTECTED; do
    if [[ "$1" == *"$f"* ]]; then
        echo "[HOOK] WARN: Editing protected config: $f"
        echo "[HOOK] Provide justification in commit message"
    fi
done
exit 0