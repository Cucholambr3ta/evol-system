#!/usr/bin/env bash
# Lint workflows for syntax and required fields

WF_DIR="${1:-.agent/workflows}"
ERRORS=0

for wf in "$WF_DIR"/*.md; do
    [ -f "$wf" ] || continue

    # Check frontmatter
    if ! head -10 "$wf" | grep -q "^---"; then
        echo "[LINT] WARN: $wf missing frontmatter"
        ERRORS=$((ERRORS+1))
    fi

    # Check required fields
    for field in name description trigger; do
        if ! grep -q "^$field:" "$wf"; then
            echo "[LINT] WARN: $wf missing '$field'"
            ERRORS=$((ERRORS+1))
        fi
    done
done

if [ $ERRORS -gt 0 ]; then
    echo "[LINT] $ERRORS warnings"
    exit 1
fi

echo "[LINT] OK: $(ls "$WF_DIR"/*.md 2>/dev/null | wc -l) workflows validated"
exit 0