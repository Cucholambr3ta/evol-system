#!/usr/bin/env bash
set -e

EVOL_VERSION="0.1.0-dev"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Evol-DD Doctor v${EVOL_VERSION} ==="
echo ""

# Mode detection
check_mode() {
    if command -v mempalace >/dev/null 2>&1; then
        echo -e "${GREEN}[COMPLETO]${NC} MemPalace CLI detected"
        echo "memory_mode: active"
    elif [ -f ~/.local/bin/mempalace ] || [ -f ~/.venv/bin/mempalace ]; then
        echo -e "${GREEN}[COMPLETO]${NC} MemPalace found in ~/.local/bin or ~/.venv/bin"
        echo "memory_mode: active"
    else
        echo -e "${YELLOW}[BASE]${NC} MemPalace not found — running in BASE mode"
        echo "memory_mode: inactive"
    fi
}

# Dependencies
check_deps() {
    echo "--- Dependencies ---"
    local errors=0
    
    if command -v git >/dev/null 2>&1; then
        echo -e "${GREEN}[OK]${NC} git $(git --version | cut -d' ' -f3)"
    else
        echo -e "${RED}[ERROR]${NC} git not found"
        errors=$((errors+1))
    fi
    
    if command -v python3 >/dev/null 2>&1; then
        local py_ver=$(python3 --version | cut -d' ' -f2)
        local py_major=$(echo $py_ver | cut -d. -f1)
        local py_minor=$(echo $py_ver | cut -d. -f2)
        if [ "$py_major" -eq 3 ] && [ "$py_minor" -ge 10 ]; then
            echo -e "${GREEN}[OK]${NC} python3 $py_ver"
        else
            echo -e "${RED}[ERROR]${NC} python3 $py_ver (requires 3.10+)"
            errors=$((errors+1))
        fi
    else
        echo -e "${RED}[ERROR]${NC} python3 not found"
        errors=$((errors+1))
    fi
    
    if command -v mempalace >/dev/null 2>&1; then
        echo -e "${GREEN}[OK]${NC} mempalace CLI"
    else
        echo -e "${YELLOW}[WARN]${NC} mempalace not in PATH (optional)"
        echo "  Searched: PATH, ~/.local/bin, ~/.venv/bin"
    fi
    
    echo ""
    return $errors
}

# Structure check
check_structure() {
    echo "--- Project Structure ---"
    local missing=0
    
    for dir in .agent/hooks scripts prompts/agents/core templates docs schemas; do
        if [ -d "$REPO_ROOT/$dir" ]; then
            echo -e "${GREEN}[OK]${NC} $dir/"
        else
            echo -e "${RED}[WARN]${NC} $dir/ missing"
            missing=$((missing+1))
        fi
    done
    
    for file in AGENTS.md CLAUDE.md evol.profile.yml evol.config.yml; do
        if [ -f "$REPO_ROOT/$file" ]; then
            echo -e "${GREEN}[OK]${NC} $file"
        else
            echo -e "${RED}[WARN]${NC} $file missing"
            missing=$((missing+1))
        fi
    done
    
    echo ""
    return $missing
}

# Legacy artifact check (Evol-DD strict mode — no xdd-*, no .xdd/)
check_legacy_artifacts() {
    echo "--- Legacy Artifact Detection ---"
    local found=0

    for artifact in xdd.profile.yml .xdd/ xdd-init.sh xdd-doctor.sh xdd-gate.py mcp.json; do
        if [ -e "$REPO_ROOT/$artifact" ]; then
            echo -e "${YELLOW}[WARN]${NC} Legacy artefact detected: $artifact"
            found=$((found+1))
        fi
    done

    if [ $found -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} No legacy artefacts detected"
    fi

    echo ""
    return 0
}

# Main
MODE_JSON=false
if [ "$1" = "--json" ]; then
    MODE_JSON=true
fi

check_mode
check_deps
check_structure
check_legacy_artifacts

echo "=== Doctor Complete ==="
exit 0
