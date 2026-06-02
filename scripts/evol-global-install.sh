#!/usr/bin/env bash
set -e

INSTALL_DIR="${HOME}/.local/bin"
EVOL_INIT="${INSTALL_DIR}/evol"

echo "[evol-install] Installing global wrapper..."

mkdir -p "$INSTALL_DIR"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cat > "$EVOL_INIT" << 'WRAPPER'
#!/usr/bin/env bash
# Evol-DD Global Wrapper
# Auto-generated — do not edit

EVOL_VERSION="0.1.0-dev"

if [ -f "$(dirname "$0")/../share/evol-dd/scripts/evol-init.sh" ]; then
    exec "$(dirname "$0")/../share/evol-dd/scripts/evol-init.sh" "$@"
elif [ -f "/usr/local/share/evol-dd/scripts/evol-init.sh" ]; then
    exec "/usr/local/share/evol-dd/scripts/evol-init.sh" "$@"
else
    echo "[evol] Error: framework not found in standard locations"
    echo "[evol] Run: git clone https://github.com/Cucholambr3ta/evol-system.git"
    echo "[evol] Then: cd evol-dd && bash scripts/evol-global-install.sh"
    exit 1
fi
WRAPPER

chmod +x "$EVOL_INIT"
echo "[evol-install] Installed to: $EVOL_INIT"
echo "[evol-install] Run: evol --help"
