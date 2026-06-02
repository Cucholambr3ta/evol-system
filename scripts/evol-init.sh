#!/usr/bin/env bash
set -e

EVOL_VERSION="0.1.0-dev"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

show_usage() {
    echo "Usage: $0 <destination> [--profile=<profile>] [--pip-mode] [--legacy]"
    echo "  --profile=<profile>  Installation profile: minimal, core, developer, security, research, full, lean"
    echo "  --pip-mode           Use pip-installed framework"
    echo "  --legacy             Use legacy mode (full copy)"
    echo "  --list-profiles      Show available profiles"
}

list_profiles() {
    echo "Available profiles:"
    echo "  minimal     - Core minimum with lessons and memory"
    echo "  core        - Standard for projects (DEFAULT)"
    echo "  developer   - Active development with ephemeral agents"
    echo "  security    - Security focus with SecDD"
    echo "  research    - Research and evolution"
    echo "  full        - Complete installation"
    echo "  lean        - Lightweight, requires global install"
}

main() {
    local dest=""
    local profile="core"
    local mode="legacy"
    
    while [ $# -gt 0 ]; do
        case "$1" in
            --profile=*) profile="${1#*=}"; shift ;;
            --pip-mode) mode="pip"; shift ;;
            --legacy) mode="legacy"; shift ;;
            --list-profiles) list_profiles; exit 0 ;;
            --help) show_usage; exit 0 ;;
            -*) shift ;;
            *) dest="$1"; shift ;;
        esac
    done
    
    if [ -z "$dest" ]; then
        show_usage
        exit 1
    fi
    
    echo "[evol-init] Destination: $dest"
    echo "[evol-init] Profile: $profile"
    echo "[evol-init] Mode: $mode"
    
    # Ensure destination exists
    mkdir -p "$dest"
    cd "$dest"
    
    # Generate .gitignore first (per PROMPT.md line 55)
    if [ ! -f .gitignore ]; then
        cat > .gitignore << 'EOF'
# Framework Evol-DD
scripts/
prompts/
skills/
templates/
evals/
schemas/
src/
tests/
.github/

# IDE configs
.claude/
.opencode/
.cursor/
.windsurf/
.agents/
.antigravity/
.codex/
.github/prompts/
.github/workflows/

# Runtime
.evol/
.xdd/
dialog/
tool_result/

# Python
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.venv/

# OS
.DS_Store

# Override (version these)
!memoria.md
!lecciones.md
!memory/
!evol.profile.yml
!CLAUDE.md
!AGENTS.md
!.agent/hooks/
!.agent/workflows/
!docs/
EOF
        echo "[evol-init] .gitignore created"
    fi
    
    # Create essential files
    for f in memoria.md lecciones.md evol.profile.yml; do
        if [ ! -f "$f" ]; then
            cp "$REPO_ROOT/templates/$(basename $f .md).template.md" "$f" 2>/dev/null || touch "$f"
        fi
    done
    
    # Init git if not exists
    if [ ! -d .git ]; then
        git init
        git checkout -b main 2>/dev/null || true
    fi
    
    echo "[evol-init] Bootstrap complete"
    echo ""
    echo "Next steps:"
    echo "  1. cd $dest"
    echo "  2. Edit memoria.md with project identity"
    echo "  3. Run: bash ./scripts/evol-doctor.sh"
}

main "$@"
