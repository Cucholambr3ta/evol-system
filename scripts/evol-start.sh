#!/usr/bin/env bash
# evol-start.sh — Arranca Evol-DD: detecta modo (COMPLETO/BASE) e indexa Memoria Persistente.
set -eu

EVOL_DATA="${EVOL_DATA_DIR:-"$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/.." && pwd )"}"
VERSION="$(cat "$EVOL_DATA/VERSION" 2>/dev/null || echo "0.1.x")"
REPO_ROOT="$(pwd)"

echo "=== Evol-DD v${VERSION} ==="
echo "[evol-start] Proyecto: $REPO_ROOT"

# === Dynamic Profile Resolution ===
if [ -f "$EVOL_DATA/manifests/workflow-profiles.json" ] && [ -f "$REPO_ROOT/evol.profile.yml" ]; then
    REQUIRED_INSTALL_PROFILE=$(python3 -c "
import json, sys, yaml

try:
    with open('$EVOL_DATA/manifests/workflow-profiles.json') as f:
        manifest = json.load(f)
    with open('$REPO_ROOT/evol.profile.yml') as f:
        current_profile = yaml.safe_load(f).get('profile', 'minimal')
except Exception as e:
    sys.exit(0)

args = sys.argv[1:]
trigger = next((arg for arg in args if not arg.startswith('-')), None)

target_install = 'minimal'
target_hook = 'standard'

if trigger:
    for m in manifest.get('mappings', []):
        if m['trigger'] == trigger:
            target_install = m['install_profile']
            target_hook = m['hook_profile']
            break

hierarchy = ['minimal', 'core', 'developer', 'security', 'research', 'full']
try:
    current_idx = hierarchy.index(current_profile)
except ValueError:
    current_idx = 0

try:
    target_idx = hierarchy.index(target_install)
except ValueError:
    target_idx = 0

if target_idx > current_idx:
    print(f'{target_install}:{target_hook}')
else:
    print(f'OK:{target_hook}')
" "$@" 2>/dev/null)

    if [ -n "$REQUIRED_INSTALL_PROFILE" ] && [ "$REQUIRED_INSTALL_PROFILE" != "OK" ]; then
        INSTALL_P=$(echo "$REQUIRED_INSTALL_PROFILE" | cut -d: -f1)
        HOOK_P=$(echo "$REQUIRED_INSTALL_PROFILE" | cut -d: -f2)
        
        if [ "$INSTALL_P" != "OK" ] && [ "$INSTALL_P" != "minimal" ]; then
            echo "[evol-start] Auto-provisioning: Escalating to installation profile '$INSTALL_P' (current profile is lower)..."
            bash "$EVOL_DATA/scripts/evol-init.sh" "$REPO_ROOT" --profile="$INSTALL_P" --upgrade
        fi
        
        echo "[evol-start] Hook profile configured: EVOL_HOOK_PROFILE=$HOOK_P"
        export EVOL_HOOK_PROFILE="$HOOK_P"
    fi
fi

# Detectar Memoria Persistente (3.x usa 'mine', versiones anteriores usaban 'index')
if command -v Memoria Persistente >/dev/null 2>&1; then
    MP_VERSION=$(Memoria Persistente --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "0.0")
    MP_MAJOR=$(echo "$MP_VERSION" | cut -d. -f1)

    echo "[Modo] COMPLETO — Memoria Persistente ${MP_VERSION} activo"

    # Inicializar wing evol-dd si no existe
    if ! Memoria Persistente status 2>/dev/null | grep -q "evol-dd"; then
        echo "[Memoria Persistente] Inicializando wing 'evol-dd'..."
        Memoria Persistente init --wing evol-dd 2>/dev/null || true
    fi

    # Indexar con mine (v3+). Requiere LLM local (Ollama) para semantica completa.
    # Sin LLM: indexado heuristico basico — igualmente util para busqueda.
    echo "[Memoria Persistente] Indexando proyecto (wing: evol-dd)..."
    if [ "$MP_MAJOR" -ge 3 ]; then
        if Memoria Persistente mine "$REPO_ROOT" --wing evol-dd --mode projects 2>/dev/null; then
            echo "[Memoria Persistente] Indexado completo."
        else
            echo "[Memoria Persistente] Indexado heuristico (sin LLM local — instalar Ollama para semantica completa)."
        fi
    else
        Memoria Persistente index --wing evol-dd --path "$REPO_ROOT" 2>/dev/null || true
    fi

    # Cargar contexto de ultima sesion
    echo "[Memoria Persistente] Buscando sesion anterior..."
    LAST=$(Memoria Persistente search "evol-dd session" --wing evol-dd 2>/dev/null | head -3 || echo "")
    if [ -n "$LAST" ]; then
        echo "$LAST"
    else
        echo "[Memoria Persistente] Sin sesion previa encontrada — primera sesion."
    fi

else
    echo "[Modo] BASE — Memoria Persistente no encontrado en PATH"
    echo "[evol-start] Instalar Memoria Persistente para Memoria Persistente: pip install Memoria Persistente"
fi

# Cargar memoria conversacional si está activa
if [ "${EVOL_MEMORY:-0}" = "1" ] && command -v python3 >/dev/null 2>&1; then
    SCRIPTS_DIR="$EVOL_DATA/scripts"
    if [ -f "$SCRIPTS_DIR/evol-memory.py" ]; then
        echo "[AGENT_MEMORY] Cargando memoria conversacional..."
        python3 "$SCRIPTS_DIR/evol-memory.py" load 2>/dev/null || true
    fi
fi

echo ""
echo "[evol-start] Sistema listo. Trigger: /evol"
echo "[evol-start] Diagnostico: evol doctor"
