#!/usr/bin/env bash
set -e

EVOL_VERSION="0.1.0-dev"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILES_MANIFEST="${REPO_ROOT}/manifests/install-profiles.json"
MODULES_MANIFEST="${REPO_ROOT}/manifests/install-modules.json"
GITIGNORE_TEMPLATE="${REPO_ROOT}/templates/gitignore.template"
AGENT_MANIFEST="${REPO_ROOT}/agent.yaml"

show_usage() {
    echo "Usage: $0 <destination> [--profile=<profile>] [--pip-mode]"
    echo "  --profile=<profile>  Installation profile: minimal, core, developer, security, research, full, lean"
    echo "  --mcp-servers=...    Comma-separated list of MCP servers (e.g. github,gitnexus)"
    echo "  --pip-mode           Use pip-installed framework"
    echo "  --list-profiles      Show available profiles"
    echo "  --explain=<profile>  Show modules for a profile"
    echo "  --dry-run            Show what would be installed without installing"
    echo "  --upgrade            Only install missing files and merge modules into existing profile"
}

list_profiles() {
    if [ ! -f "$PROFILES_MANIFEST" ]; then
        echo "[error] Profiles manifest not found: $PROFILES_MANIFEST"
        exit 1
    fi

    echo "Available profiles:"
    local ids
    ids=$(python3 -c "
import json, sys
with open('$PROFILES_MANIFEST') as f:
    data = json.load(f)
for p in data['profiles']:
    print(f\"  {p['id']:12} - {p['description']}\")
" 2>/dev/null) || echo "  minimal     - Core minimum with lessons and memory"
    echo "$ids"
}

explain_profile() {
    local profile="$1"
    if [ -z "$profile" ]; then
        echo "[error] --explain requires a profile name"
        exit 1
    fi

    python3 -c "
import json, sys

with open('$PROFILES_MANIFEST') as f:
    profiles = json.load(f)['profiles']
with open('$MODULES_MANIFEST') as f:
    modules = json.load(f)['modules']

def resolve(profile_id, seen=None):
    if seen is None:
        seen = set()
    if profile_id in seen:
        return []
    seen.add(profile_id)

    p = next((x for x in profiles if x['id'] == profile_id), None)
    if not p:
        return []

    result = []
    if 'extends' in p:
        result.extend(resolve(p['extends'], seen))
    result.extend(p.get('modules', []))
    return result

all_modules = resolve('$profile')
print(f\"Profile: $profile\")
print(f\"Modules: {len(all_modules)}\")
print()
for m in sorted(all_modules):
    desc = modules.get(m, {}).get('description', 'No description')
    print(f\"  - {m}: {desc}\")
" 2>/dev/null || echo "[error] Could not explain profile"
}

resolve_modules() {
    local profile="$1"
    python3 -c "
import json, sys

with open('$PROFILES_MANIFEST') as f:
    profiles = json.load(f)['profiles']

def resolve(profile_id, seen=None):
    if seen is None:
        seen = set()
    if profile_id in seen:
        return []
    seen.add(profile_id)

    p = next((x for x in profiles if x['id'] == profile_id), None)
    if not p:
        return []

    result = []
    if 'extends' in p:
        result.extend(resolve(p['extends'], seen))
    result.extend(p.get('modules', []))
    return result

modules = resolve('$profile')
print(' '.join(modules))
" 2>/dev/null
}

verify_manifest() {
    if [ ! -f "$AGENT_MANIFEST" ]; then
        echo "[warn] agent.yaml not found. Framework may be incomplete."
        return 0
    fi

    if command -v python3 >/dev/null 2>&1; then
        local profile_ok
        profile_ok=$(python3 -c "
import yaml, sys
try:
    with open('$AGENT_MANIFEST') as f:
        m = yaml.safe_load(f)
    profiles_in_manifest = set(m.get('install_profiles', {}).keys())
    profile = '$profile'
    if profile not in profiles_in_manifest:
        print(f'[warn] Profile \"{profile}\" not in agent.yaml manifest')
        sys.exit(1)
except Exception as e:
    print(f'[warn] Could not verify manifest: {e}')
    sys.exit(0)
" 2>/dev/null) || profile_ok=0

        if [ $? -eq 0 ] && [ -n "$profile_ok" ]; then
            echo "[init] Manifest verified: profile '$profile' found in agent.yaml"
        fi
    fi
}

install_files_for_module() {
    local module="$1"
    local dest="$2"
    local upgrade="$3"

    python3 -c "
import json, os, sys

with open('$MODULES_MANIFEST') as f:
    data = json.load(f)

module = '$module'
mod_data = data['modules'].get(module, {})
if not mod_data:
    print(f'[warn] Module not found: {module}', file=sys.stderr)
    sys.exit(0)

src_dir = '$REPO_ROOT'
dest_dir = '$dest'
upgrade = '$upgrade' == 'true'

for f in mod_data.get('files', []):
    src = os.path.join(src_dir, f)
    dst = os.path.join(dest_dir, f)
    if os.path.exists(src):
        if upgrade and os.path.exists(dst):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        import shutil
        shutil.copy2(src, dst)
        print(f'  + {f}')

for d in mod_data.get('dirs', []):
    src = os.path.join(src_dir, d.rstrip('/'))
    dst = os.path.join(dest_dir, d.rstrip('/'))
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        import shutil
        if os.path.isdir(src):
            if upgrade:
                for root, _, files in os.walk(src):
                    for file in files:
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, src)
                        dst_file = os.path.join(dst, rel_path)
                        if not os.path.exists(dst_file):
                            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                            shutil.copy2(src_file, dst_file)
                            print(f'  + {os.path.join(d, rel_path)}')
            else:
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f'  + {d}/*')
" 2>/dev/null
}

main() {
    local dest=""
    local profile="core"
    local mode="pip"
    local dry_run=false
    local upgrade=false
    local profile_passed=false
    local opt_mcp_servers=""

    while [ $# -gt 0 ]; do
        case "$1" in
            --profile=*) profile="${1#*=}"; profile_passed=true; shift ;;
            --mcp-servers=*) opt_mcp_servers="${1#*=}"; shift ;;
            --pip-mode) mode="pip"; shift ;;
            --list-profiles) list_profiles; exit 0 ;;
            --explain=*) explain_profile "${1#*=}"; exit 0 ;;
            --dry-run) dry_run=true; shift ;;
            --upgrade) upgrade=true; shift ;;
            --help) show_usage; exit 0 ;;
            -*) shift ;;
            *) dest="$1"; shift ;;
        esac
    done

    if [ -z "$dest" ]; then
        show_usage
        exit 1
    fi

    if [ "$upgrade" = true ] && [ "$profile_passed" != true ] && [ -f "$dest/evol.profile.yml" ]; then
        if command -v python3 >/dev/null 2>&1; then
            local current_profile
            current_profile=$(python3 -c "
import sys
try:
    import yaml
    with open('$dest/evol.profile.yml') as f:
        data = yaml.safe_load(f) or {}
    print(data.get('profile', 'core'))
except:
    print('core')
" 2>/dev/null)
            profile="${current_profile:-core}"
            echo "[evol-init] Upgrade mode: Using existing profile '$profile'"
        fi
    fi

    echo "[evol-init] Destination: $dest"
    echo "[evol-init] Profile: $profile"

    # Validate profile exists
    if ! python3 -c "
import json
with open('$PROFILES_MANIFEST') as f:
    profiles = json.load(f)['profiles']
ids = [p['id'] for p in profiles]
if '$profile' not in ids:
    print(f'[error] Unknown profile: $profile', file=sys.stderr)
    print(f'[error] Available: {\" \".join(ids)}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
        echo "[error] Profile validation failed"
        exit 1
    fi

    if [ "$dry_run" = true ]; then
        echo "[dry-run] Would install profile: $profile"
        local modules
        modules=$(resolve_modules "$profile")
        echo "Modules: $modules"
        exit 0
    fi

    # Ensure destination exists
    mkdir -p "$dest"
    cd "$dest"

    # Copy gitignore template
    if [ ! -f .gitignore ] && [ -f "$GITIGNORE_TEMPLATE" ]; then
        cp "$GITIGNORE_TEMPLATE" .gitignore
        echo "[evol-init] .gitignore created from template"
    fi

    # Resolve and install modules
    local modules
    modules=$(resolve_modules "$profile")

    echo "[evol-init] Installing modules: $modules"

    verify_manifest

    for module in $modules; do
        echo "  Module: $module"
        install_files_for_module "$module" "." "$upgrade"
    done

    # Write active profile to evol.profile.yml
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "
import json, os

with open('$PROFILES_MANIFEST') as f:
    profiles = json.load(f)['profiles']

def resolve(profile_id, seen=None):
    if seen is None:
        seen = set()
    if profile_id in seen:
        return []
    seen.add(profile_id)
    p = next((x for x in profiles if x['id'] == profile_id), None)
    if not p:
        return []
    result = []
    if 'extends' in p:
        result.extend(resolve(p['extends'], seen))
    result.extend(p.get('modules', []))
    return result

modules = resolve('$profile')
data = {}
profile_path = os.path.join(os.getcwd(), 'evol.profile.yml')
upgrade = '$upgrade' == 'true'

if os.path.exists(profile_path):
    try:
        import yaml
        with open(profile_path) as f:
            data = yaml.safe_load(f) or {}
    except:
        pass

if upgrade:
    existing_modules = data.get('modules', [])
    data['modules'] = list(set(existing_modules + modules))
    if 'profile' not in data:
        data['profile'] = '$profile'
else:
    data['profile'] = '$profile'
    data['modules'] = modules

with open(profile_path, 'w') as f:
    import yaml
    yaml.dump(data, f, default_flow_style=False)

print(f'[evol-init] Profile $profile saved to evol.profile.yml')
" 2>/dev/null || echo "[evol-init] evol.profile.yml updated (YAML write skipped)"
    fi

    # Escribir configuración de MCP siempre (default)
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "
import yaml, os
config_path = os.path.join(os.getcwd(), 'evol.config.yml')
data = {}
if os.path.exists(config_path):
    try:
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
    except:
        pass

if 'mcp' not in data:
    data['mcp'] = {}
data['mcp']['enabled'] = True

if 'servers' not in data['mcp']:
    data['mcp']['servers'] = {}

servers_str = '$opt_mcp_servers'
if servers_str:
    for s in servers_str.split(','):
        s = s.strip()
        if s and s not in data['mcp']['servers']:
            data['mcp']['servers'][s] = {
                'command': 'npx',
                'args': ['-y', f'@modelcontextprotocol/server-{s}' if s != 'gitnexus' else 'gitnexus']
            }

with open(config_path, 'w') as f:
    yaml.dump(data, f, default_flow_style=False)

print('[evol-init] MCP habilitado por defecto en evol.config.yml')
" 2>/dev/null || echo "[evol-init] Error guardando evol.config.yml"
    fi

    # Estructura /acuerdos (cero deuda tecnica — base del briefing arbol 16 dimensiones)
    if [ ! -d ./acuerdos ]; then
        mkdir -p acuerdos/idea acuerdos/discovery acuerdos/research acuerdos/design \
                 acuerdos/wireframes acuerdos/proyecto \
                 acuerdos/memoria acuerdos/lecciones
        printf "# Idea\n\nIdea decantada en atomos (por /evol idea). 1 atomo por tema/proyecto/link.\n" \
            > acuerdos/idea/README.md
        printf "# Discovery\n\nResearch PRE-briefing: investigacion por tema para ENTENDER la idea\n(por /evol discovery). Distinto de research/ (post-briefing, como construir).\n" \
            > acuerdos/discovery/README.md
        printf "# INDEX — Idea decantada\n\n> Solicitud del usuario decantada en atomos. Cada uno dispara discovery.\n\n| Atomo | Tema | Fuente | Artefacto discovery |\n|-------|------|--------|---------------------|\n" \
            > acuerdos/idea/INDEX.md
        printf "# INDEX — Discovery\n\n> Que entendio el agente de la idea, tras investigar cada tema.\n\n| Tema | Que es | Que aporta | Decision sugerida |\n|------|--------|-----------|-------------------|\n" \
            > acuerdos/discovery/INDEX.md
        printf "# Research\n\nInvestigacion por dominio tecnico POST-briefing: como construir cada dominio\n(en doc-granular). Distinto de discovery/ (pre-briefing, entender la idea).\n" \
            > acuerdos/research/README.md
        printf "# Design System\n\ntokens.md + components.md + assets.md (Dimension 15 del briefing).\n" \
            > acuerdos/design/README.md
        printf "# Wireframes\n\nHTML aprobado por pantalla (Dimension 16). Regla de diseno inmutable.\n" \
            > acuerdos/wireframes/README.md
        printf "# Proyecto\n\nN documentos granulares por dominio tecnico (generados post-briefing).\n" \
            > acuerdos/proyecto/README.md
        printf "# Memoria por Sprint\n\nGenerados con: evol-memory --project=. sprint-close --sprint=NN\n" \
            > acuerdos/memoria/README.md
        printf "# Lecciones por Sprint\n\nGenerados con: evol-memory --project=. sprint-close --sprint=NN\n" \
            > acuerdos/lecciones/README.md
        echo "[evol-init] acuerdos/ creado (7 subcarpetas — base para /evol briefing)."
    fi

    # MEMORY.md atomico: 3 atomos + agregado (idempotente)
    mkdir -p acuerdos/memoria acuerdos/lecciones
    [ -f acuerdos/memoria/decisiones.md ] || printf "# Decisiones clave\n\n> Atomo de MEMORY. Decisiones de arquitectura y producto persistentes.\n\n-\n" > acuerdos/memoria/decisiones.md
    [ -f acuerdos/memoria/convenciones.md ] || printf "# Convenciones\n\n> Atomo de MEMORY. Estandares de codigo y patrones.\n\n-\n" > acuerdos/memoria/convenciones.md
    [ -f acuerdos/memoria/riesgos.md ] || printf "# Riesgos activos\n\n> Atomo de MEMORY. Riesgos vigentes y mitigaciones.\n\n-\n" > acuerdos/memoria/riesgos.md
    if [ ! -f acuerdos/lecciones/INDEX.md ]; then
        printf "# INDEX — Lecciones por Sprint\n\n> Indice de lecciones separadas por sprint.\n\n| Sprint | Archivo | Fecha cierre |\n|--------|---------|-------------|\n" \
            > acuerdos/lecciones/INDEX.md
    fi

    # Esqueleto de carpetas atomicas (ADR atomicidad — idempotente)
    _seed_atomic_index() {
        local dir="$1" titulo="$2"
        mkdir -p "$dir"
        [ -f "$dir/INDEX.md" ] || printf "# INDEX — %s\n\n> Indice atomico. 1 doc = 1 concepto.\n\n| Documento | Resumen | Trazabilidad |\n|-----------|---------|-------------|\n" "$titulo" > "$dir/INDEX.md"
        [ -f "$dir/INDEX.json" ] || printf '{\n  "dominio": "%s",\n  "docs": [],\n  "total_docs": 0,\n  "total_tokens_md": 0\n}\n' "$(basename "$dir")" > "$dir/INDEX.json"
    }
    _seed_atomic_index "acuerdos/sprints"       "Plan de Sprints"
    _seed_atomic_index "docs/features"          "Catalogo de Features (FDD)"
    _seed_atomic_index "docs/domain"            "Modelo de Dominio (DDD)"
    _seed_atomic_index "docs/privacy"           "Inventario de Privacidad (PII)"
    _seed_atomic_index "api/openapi/fragments"  "Fragmentos OpenAPI por recurso"
    [ -f docs/domain/UBIQUITOUS_LANGUAGE.md ] || printf "# Ubiquitous Language\n\n> Glosario del dominio. Vocabulario obligatorio.\n\n| Termino | Definicion | Sinonimos prohibidos |\n|---------|------------|---------------------|\n" > docs/domain/UBIQUITOUS_LANGUAGE.md
    echo "[evol-init] ✓ esqueleto atomico creado (sprints/, features/, domain/, privacy/, openapi/ + 3 atomos MEMORY)."

    # Init git if not exists
    if [ ! -d .git ]; then
        git init
        git checkout -b main 2>/dev/null || true
        echo "[evol-init] git initialized with main branch"
    fi

    echo ""
    echo "[evol-init] Bootstrap complete"
    echo ""
    echo "Next steps:"
    echo "  1. cd $dest"
    echo "  2. Edit memoria.md with project identity"
    echo "  3. Run: bash ./scripts/evol-doctor.sh"
    echo ""
    echo "Profile installed: $profile"
}

main "$@"