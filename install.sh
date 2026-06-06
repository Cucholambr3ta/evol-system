#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Evol-DD Installer — Cross-platform curl | bash
# Installs Python (if needed), pipx, evol-dd[memory,graph] and IDE triggers.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Cucholambr3ta/evol-system/main/install.sh | bash
#   curl -fsSL ... | bash -s -- --no-ide
#   curl -fsSL ... | bash -s -- --profile developer
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
EVOL_VERSION="${EVOL_VERSION:-latest}"
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=10
NO_IDE=0
PROFILE="developer"
DRY_RUN=0

# ── Parse args ────────────────────────────────────────────────────────────────
for arg in "$@"; do
    case "$arg" in
        --no-ide)      NO_IDE=1 ;;
        --dry-run)     DRY_RUN=1 ;;
        --profile=*)   PROFILE="${arg#*=}" ;;
        --help|-h)
            echo "Usage: install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-ide          Skip IDE trigger installation"
            echo "  --profile=NAME    Installation profile (default: developer)"
            echo "  --dry-run         Show what would be done without doing it"
            echo "  --help, -h        Show this help"
            echo ""
            echo "Profiles: minimal, core, developer, security, research, full, lean"
            exit 0
            ;;
    esac
done

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[i]${NC} $*"; }
success() { echo -e "${GREEN}[✓]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
error()   { echo -e "${RED}[✗]${NC} $*" >&2; }
step()    { echo -e "\n${BLUE}── Step $1: $2 ──${NC}"; }

# ── Version comparison ────────────────────────────────────────────────────────
version_ge() {
    # Returns 0 if $1 >= $2
    printf '%s\n%s' "$2" "$1" | sort -V -C
}

# ── Step 1: Detect OS ────────────────────────────────────────────────────────
step 1 "Detecting OS"
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux*)   OS_NAME="linux"  ;;
    Darwin*)  OS_NAME="macos"  ;;
    MINGW*|MSYS*|CYGWIN*) OS_NAME="wsl" ;;
    *)        OS_NAME="unknown" ;;
esac

info "OS: $OS_NAME ($ARCH)"

if [[ "$OS_NAME" == "unknown" ]]; then
    error "Unsupported OS: $OS"
    error "Supported: Linux, macOS, WSL"
    exit 1
fi

# ── Step 2: Detect/Install Python ────────────────────────────────────────────
step 2 "Ensuring Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+"

python_cmd=""
python_version=""

find_python() {
    for cmd in python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver="$($cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)"
            if [[ -n "$ver" ]]; then
                local major minor
                major="${ver%%.*}"
                minor="${ver##*.}"
                if [[ "$major" -ge "$MIN_PYTHON_MAJOR" ]] && [[ "$minor" -ge "$MIN_PYTHON_MINOR" ]]; then
                    python_cmd="$cmd"
                    python_version="$ver"
                    return 0
                fi
            fi
        fi
    done
    return 1
}

install_python_linux() {
    info "Attempting to install Python via system package manager..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq python3 python3-pip python3-venv python3-dev
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip python3-devel
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3 python3-pip python3-devel
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm python python-pip
    elif command -v zypper &>/dev/null; then
        sudo zypper install -y python3 python3-pip python3-devel
    else
        error "Cannot detect package manager. Install Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+ manually."
        error "  https://www.python.org/downloads/"
        exit 1
    fi
}

install_python_macos() {
    if command -v brew &>/dev/null; then
        info "Installing Python via Homebrew..."
        brew install python@3.12
    else
        error "Homebrew not found."
        error "Install it: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
}

if find_python; then
    success "Python $python_version found: $(command -v "$python_cmd")"
else
    warn "Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+ not found"
    if [[ "$DRY_RUN" -eq 1 ]]; then
        info "[dry-run] Would install Python"
    else
        case "$OS_NAME" in
            linux) install_python_linux ;;
            macos) install_python_macos ;;
            wsl)   install_python_linux ;;
        esac
        if find_python; then
            success "Python $python_version installed"
        else
            error "Python installation failed. Install manually: https://www.python.org/downloads/"
            exit 1
        fi
    fi
fi

# ── Step 3: Detect/Install pipx ──────────────────────────────────────────────
step 3 "Ensuring pipx"

if command -v pipx &>/dev/null; then
    success "pipx detected: $(command -v pipx)"
else
    warn "pipx not found"
    if [[ "$DRY_RUN" -eq 1 ]]; then
        info "[dry-run] Would install pipx"
    else
        info "Installing pipx..."
        "$python_cmd" -m pip install --user pipx 2>/dev/null || "$python_cmd" -m pip install pipx
        "$python_cmd" -m pipx ensurepath 2>/dev/null || true

        # Ensure pipx is in PATH for this session
        export PATH="$HOME/.local/bin:$HOME/.local/pipx/venvs:$PATH"

        if command -v pipx &>/dev/null; then
            success "pipx installed"
        else
            error "pipx installation failed"
            error "Try: python3 -m pip install --user pipx"
            exit 1
        fi
    fi
fi

# ── Step 4: Install evol-dd ──────────────────────────────────────────────────
step 4 "Installing evol-dd[full]"

EXTRAS="memory,graph"
info "Installing with extras: $EXTRAS"

if [[ "$DRY_RUN" -eq 1 ]]; then
    info "[dry-run] Would run: pipx install evol-dd[$EXTRAS]"
else
    # Remove existing installation if present
    pipx uninstall evol-dd 2>/dev/null || true

    pipx install "evol-dd[$EXTRAS]" --force 2>&1 || {
        warn "pipx install with extras failed, trying pip..."
        "$python_cmd" -m pip install --user "evol-dd[$EXTRAS]"
    }

    # Verify installation
    if command -v evol &>/dev/null || pipx list 2>/dev/null | grep -q evol-dd; then
        success "evol-dd installed"
    else
        warn "evol-dd installed but 'evol' command not in PATH"
        info "You may need to add ~/.local/bin to your PATH"
    fi
fi

# ── Step 5: Verify dependencies ──────────────────────────────────────────────
step 5 "Verifying dependencies"

verify_dep() {
    local name="$1"
    local import="$2"
    if "$python_cmd" -c "import $import" 2>/dev/null; then
        success "$name OK"
    else
        warn "$name not available (optional)"
    fi
}

verify_dep "ChromaDB"  "chromadb"
verify_dep "NetworkX"  "networkx"

# ── Step 6: IDE Triggers ─────────────────────────────────────────────────────
step 6 "IDE Triggers"

if [[ "$NO_IDE" -eq 1 ]]; then
    info "Skipping IDE triggers (--no-ide)"
elif [[ "$DRY_RUN" -eq 1 ]]; then
    info "[dry-run] Would install IDE triggers"
else
    info "Installing IDE triggers..."

    # Find evol-adapt.sh
    EVOL_HOME=""
    if command -v evol &>/dev/null; then
        EVOL_HOME="$(dirname "$(command -v evol)")" 2>/dev/null || true
    fi

    # Try to find evol-adapt.sh in common locations
    for candidate in \
        "$HOME/.local/share/evol-dd/scripts/evol-adapt.sh" \
        "$(pipx environment --value PIPX_LOCAL_VENVS 2>/dev/null)/evol-dd/bin/scripts/evol-adapt.sh" \
        "$(pip show evol-dd 2>/dev/null | grep Location | cut -d' ' -f2)/evol_cli/scripts/evol-adapt.sh" \
    ; do
        if [[ -f "$candidate" ]]; then
            bash "$candidate" all 2>/dev/null || true
            success "IDE triggers installed"
            break
        fi
    done
fi

# ── Step 7: Summary ──────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Evol-DD Installation Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo ""

# Show version
if command -v evol &>/dev/null; then
    evol --version 2>/dev/null || true
fi

echo ""
info "Quick start:"
echo "  evol init /path/to/project --profile $PROFILE"
echo ""
info "Docs:"
echo "  https://github.com/Cucholambr3ta/evol-system#readme"
echo ""
info "Update:"
echo "  pipx upgrade evol-dd"
echo ""
