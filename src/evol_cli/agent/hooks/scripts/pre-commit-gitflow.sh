#!/usr/bin/env bash
# Pre-commit hook: Enforce GitFlow branch naming

BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")

if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "develop" ]; then
    exit 0
fi

ALLOWED='^(feature/|fix/|hotfix/|release/|chore/|docs/|refactor/)'
if ! [[ "$BRANCH" =~ $ALLOWED ]]; then
    echo "[HOOK] BLOCKED: Branch '$BRANCH' does not follow GitFlow convention"
    echo "[HOOK] Allowed: feature/*, fix/*, hotfix/*, release/*, chore/*, docs/*, refactor/*"
    exit 1
fi

# Check conventional commits
if [ -f ".git/COMMIT_EDITMSG" ]; then
    MSG=$(head -1 .git/COMMIT_EDITMSG)
    if ! [[ "$MSG" =~ ^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert) ]]; then
        echo "[HOOK] WARN: Commit message should follow Conventional Commits"
    fi
fi

exit 0