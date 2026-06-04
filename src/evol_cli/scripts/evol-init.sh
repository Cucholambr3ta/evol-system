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
    echo "  --pip-mode           Use pip-installed framework"
    echo "  --list-profiles      Show available profiles"
    echo "  --explain=<profile>  Show modules for a profile"
    echo "  --dry-run            Show what would be installed without installing"
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

    python3 -c "
import json, os

with open('$MODULES_MANIFEST') as f:
    data = json.load(f)

module = '$module'
mod_data = data['modules'].get(module, {})
if not mod_data:
    print(f'[warn] Module not found: {module}', file=sys.stderr)
    sys.exit(0)

src_dir = '$REPO_ROOT'
dest_dir = '$dest'

for f in mod_data.get('files', []):
    src = os.path.join(src_dir, f)
    dst = os.path.join(dest_dir, f)
    if os.path.exists(src):
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
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f'  + {d}/*')
" 2>/dev/null
}

main() {
    local dest=""
    local profile="core"
    local mode="pip"
    local dry_run=false

    while [ $# -gt 0 ]; do
        case "$1" in
            --profile=*) profile="${1#*=}"; shift ;;
            --pip-mode) mode="pip"; shift ;;
            --list-profiles) list_profiles; exit 0 ;;
            --explain=*) explain_profile "${1#*=}"; exit 0 ;;
            --dry-run) dry_run=true; shift ;;
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
        install_files_for_module "$module" "$dest"
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
if os.path.exists(profile_path):
    try:
        import yaml
        with open(profile_path) as f:
            data = yaml.safe_load(f) or {}
    except:
        pass

data['profile'] = '$profile'
data['modules'] = modules

with open(profile_path, 'w') as f:
    import yaml
    yaml.dump(data, f, default_flow_style=False)

print(f'[evol-init] Profile $profile saved to evol.profile.yml')
" 2>/dev/null || echo "[evol-init] evol.profile.yml updated (YAML write skipped)"
    fi

    # Estructura /acuerdos (cero deuda tecnica — base del briefing arbol 16 dimensiones)
    if [ ! -d ./acuerdos ]; then
        mkdir -p acuerdos/idea acuerdos/research acuerdos/design \
                 acuerdos/wireframes acuerdos/proyecto \
                 acuerdos/memoria acuerdos/lecciones
        printf "# Idea\n\nIdea original del proyecto. Ver idea.md (generado por /evol briefing).\n" \
            > acuerdos/idea/README.md
        printf "# Research\n\nInvestigacion por dominio tecnico (generada post-briefing).\n" \
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

    # MEMORY.md + INDEX.md en acuerdos/ (idempotente — crea si faltan)
    if [ ! -f acuerdos/memoria/MEMORY.md ]; then
        mkdir -p acuerdos/memoria
        printf "# MEMORY.md — Hechos persistentes del proyecto\n\n> Solo hechos duraderos, no log temporal.\n\n## Decisiones clave\n\n-\n\n## Convenciones\n\n-\n\n## Riesgos activos\n\n-\n" \
            > acuerdos/memoria/MEMORY.md
        echo "[evol-init] ✓ acuerdos/memoria/MEMORY.md creado."
    fi
    if [ ! -f acuerdos/lecciones/INDEX.md ]; then
        mkdir -p acuerdos/lecciones
        printf "# INDEX — Lecciones por Sprint\n\n> Indice de lecciones separadas por sprint.\n\n| Sprint | Archivo | Fecha cierre |\n|--------|---------|-------------|\n" \
            > acuerdos/lecciones/INDEX.md
        echo "[evol-init] ✓ acuerdos/lecciones/INDEX.md creado."
    fi

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