#!/usr/bin/env bash
# PostToolUse hook: Move docs to canonical paths

DEST="$1"
if [ -f "$DEST" ]; then
    case "$DEST" in
        *architecture*.md) [ ! -d "docs/arquitectura" ] && mkdir -p "docs/arquitectura" ;;
        *requisitos*.md) [ ! -d "docs/requisitos" ] && mkdir -p "docs/requisitos" ;;
        *qa*.md|*test*.md) [ ! -d "docs/qa" ] && mkdir -p "docs/qa" ;;
        *seguridad*.md|*security*.md) [ ! -d "docs/seguridad" ] && mkdir -p "docs/seguridad" ;;
    esac
fi
exit 0