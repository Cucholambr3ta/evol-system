#!/usr/bin/env bash

EVOL_VERSION="0.1.0-dev"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Evol-DD Start v${EVOL_VERSION} ==="

# Detect mode
if command -v mempalace >/dev/null 2>&1 || [ -f ~/.local/bin/mempalace ]; then
    echo "[Modo] COMPLETO — MemPalace active"
    echo "[MemPalace] Indexing..."
    mempalace index --wing evol-dd --path "$REPO_ROOT" 2>/dev/null || echo "[MemPalace] Index skipped"
    echo "[MemPalace] Loading last session..."
    mempalace search "last_session" 2>/dev/null | head -5 || true
else
    echo "[Modo] BASE — MemPalace not available"
fi

echo ""
echo "System ready. Trigger: /evol"
echo "Run: bash scripts/evol-doctor.sh to verify"
