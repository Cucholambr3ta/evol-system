#!/usr/bin/env bash
# SessionEnd hook: Create handoff marker for next session
# Generates a compact summary of pending work

PROJECT="${EVOL_PROJECT:-.}"
HANDOFF_FILE="acuerdos/memoria/handoff.json"

# Check if there are uncommitted changes
if command -v git &>/dev/null && git rev-parse --git-dir >/dev/null 2>&1; then
    CHANGED=$(git status --porcelain 2>/dev/null | wc -l)
    BRANCH=$(git branch --show-current 2>/dev/null)

    if [ "$CHANGED" -gt 0 ]; then
        SUMMARY="Branch: $BRANCH, $CHANGED uncommitted files"
    else
        SUMMARY="Branch: $BRANCH, clean"
    fi
else
    SUMMARY="Not a git repo or git not available"
fi

# Check pending acuerdos
PENDING_ACUERDOS=0
if [ -d "acuerdos/idea" ]; then
    PENDING_ACUERDOS=$(find acuerdos/idea -name "*.md" ! -name "README.md" ! -name "INDEX.md" 2>/dev/null | wc -l)
fi

# Create handoff marker
mkdir -p acuerdos/memoria
cat > "$HANDOFF_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "summary": "$SUMMARY",
  "pending_acuerdos": $PENDING_ACUERDOS,
  "branch": "${BRANCH:-unknown}",
  "next_action": "continuar con la fase actual del pipeline"
}
EOF

echo "[hook] Handoff marker created: $HANDOFF_FILE"
exit 0
