#!/usr/bin/env bash
set -euo pipefail

EVOL_VERSION="0.1.0-dev"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXIT_CODE=0
ISSUES=()
MODE_JSON=false

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

json_results() {
    local severity="$1"
    local check="$2"
    local message="$3"
    local path="${4:-}"
    printf '{"severity":"%s","check":"%s","message":"%s","path":"%s"}\n' \
        "$severity" "$check" "$message" "$path"
}

emit() {
    local severity="$1"
    local check="$2"
    local message="$3"
    local path="${4:-}"

    if [ "$MODE_JSON" = true ]; then
        json_results "$severity" "$check" "$message" "$path"
    else
        local color
        case "$severity" in
            CRITICAL|HIGH) color="$RED" ;;
            MEDIUM) color="$YELLOW" ;;
            LOW|INFO) color="$BLUE" ;;
            *) color="$GREEN" ;;
        esac
        printf "%b[%s]%b %s: %s\n" "$color" "$severity" "$NC" "$check" "$message"
    fi

    if [ "$severity" = "CRITICAL" ] || [ "$severity" = "HIGH" ]; then
        EXIT_CODE=1
    fi
}

check_profile() {
    local profile_file="$REPO_ROOT/evol.profile.yml"
    emit "INFO" "Profile" "Checking evol.profile.yml..."

    if [ ! -f "$profile_file" ]; then
        emit "CRITICAL" "Profile" "evol.profile.yml not found" "$profile_file"
        return
    fi

    local profile
    profile=$(grep -E '^profile:' "$profile_file" | cut -d: -f2 | tr -d ' ' || echo "")
    if [ -z "$profile" ]; then
        emit "HIGH" "Profile" "profile field missing or empty in evol.profile.yml" "$profile_file"
    else
        emit "OK" "Profile" "profile=$profile"
    fi

    local valid_profiles="minimal core developer security research full lean custom"
    if echo "$valid_profiles" | grep -qw "$profile"; then
        emit "OK" "Profile" "profile '$profile' is valid"
    else
        emit "MEDIUM" "Profile" "profile '$profile' is non-standard but accepted"
    fi
}

check_required_files() {
    emit "INFO" "RequiredFiles" "Checking mandatory files..."

    local required_files=(
        "evol.profile.yml"
        "memoria.md"
        "lecciones.md"
        "CLAUDE.md"
        "AGENTS.md"
        "docs/equipo.md"
    )

    for file in "${required_files[@]}"; do
        if [ -f "$REPO_ROOT/$file" ]; then
            emit "OK" "RequiredFiles" "exists: $file" "$file"
        else
            emit "HIGH" "RequiredFiles" "missing: $file" "$file"
        fi
    done
}

check_scripts_executable() {
    emit "INFO" "Scripts" "Checking scripts executables..."

    local scripts=(
        "scripts/evol-doctor.sh"
        "scripts/evol-init.sh"
        "scripts/evol-gate.py"
        "scripts/evol-state.py"
        "scripts/evol-shield.py"
        "scripts/evol-eval.py"
        "scripts/evol-memory.py"
        "scripts/evol-evolve.py"
        "scripts/evol-research.py"
        "scripts/evol-lessons.py"
        "scripts/evol-orchestrate.py"
        "scripts/evol-flow.py"
        "scripts/evol-provider.py"
        "scripts/evol-adapt.sh"
        "scripts/evol-brand.sh"
        "scripts/evol-start.sh"
        "scripts/evol-global-install.sh"
        "scripts/generate-equipo.sh"
    )

    local missing=0
    for script in "${scripts[@]}"; do
        if [ -f "$REPO_ROOT/$script" ]; then
            if [ -x "$REPO_ROOT/$script" ]; then
                emit "OK" "Scripts" "executable: $script" "$script"
            else
                emit "MEDIUM" "Scripts" "not executable: $script" "$script"
            fi
        fi
    done
}

check_sensitive_permissions() {
    emit "INFO" "Permissions" "Checking sensitive permissions..."

    local sensitive_files=(
        ".evol/.gate-key"
        ".evol/.gate-log.jsonl"
    )

    for path in "${sensitive_files[@]}"; do
        if [ -e "$REPO_ROOT/$path" ]; then
            local perms
            perms=$(stat -c '%a' "$REPO_ROOT/$path" 2>/dev/null || stat -f '%Lp' "$REPO_ROOT/$path" 2>/dev/null || echo "")
            if [ "$perms" = "600" ]; then
                emit "OK" "Permissions" "$path is 0600: OK" "$path"
            elif [ "$perms" = "640" ]; then
                emit "OK" "Permissions" "$path is 0640: OK" "$path"
            else
                emit "HIGH" "Permissions" "$path has permissions $perms, expected 0600" "$path"
            fi
        fi
    done

    if [ -d "$REPO_ROOT/.evol" ]; then
        local dperms
        dperms=$(stat -c '%a' "$REPO_ROOT/.evol" 2>/dev/null || stat -f '%Lp' "$REPO_ROOT/.evol" 2>/dev/null || echo "")
        local valid=false
        case "$dperms" in
            700|750) valid=true ;;
        esac
        if [ "$valid" = true ]; then
            emit "OK" "Permissions" ".evol/ is $dperms: OK"
        else
            emit "MEDIUM" "Permissions" ".evol/ has permissions $dperms, expected 0700 or 0750"
        fi
    fi

    local runtime_dirs="memory dialog tool_result .agent/hooks/scripts"
    for dir in $runtime_dirs; do
        if [ -d "$REPO_ROOT/$dir" ]; then
            local dperms
            dperms=$(stat -c '%a' "$REPO_ROOT/$dir" 2>/dev/null || stat -f '%Lp' "$REPO_ROOT/$dir" 2>/dev/null || echo "")
            if [ -n "$dperms" ] && [ "$dperms" != "750" ] && [ "$dperms" != "755" ] && [ "$dperms" != "700" ]; then
                emit "MEDIUM" "Permissions" "$dir/ is group-writable ($dperms)" "$dir"
            fi
        fi
    done
}

check_source_dirs_tracked() {
    emit "INFO" "SourceTracking" "Checking framework source dirs are not ignored..."

    local critical_dirs=(
        "scripts"
        "prompts"
        "skills"
        "templates"
        "evals"
        "schemas"
        "src"
        "tests"
        ".github/workflows"
        ".agent/hooks/scripts"
    )

    for dir in "${critical_dirs[@]}"; do
        if [ -d "$REPO_ROOT/$dir" ]; then
            if git check-ignore -q "$dir" 2>/dev/null; then
                emit "CRITICAL" "SourceTracking" "$dir/ is ignored by .gitignore!" "$dir"
            else
                emit "OK" "SourceTracking" "$dir/ is tracked" "$dir"
            fi
        fi
    done
}

check_mempalace_safe() {
    emit "INFO" "MemPalace" "Checking MemPalace safe indexing config..."

    local config_files=(
        "mempalace.yaml"
        ".mempalace/config.yaml"
        "mempalace.yml"
        "evol.config.yml"
    )

    local found_config=""
    for cfg in "${config_files[@]}"; do
        if [ -f "$REPO_ROOT/$cfg" ]; then
            found_config="$cfg"
            break
        fi
    done

    if [ -z "$found_config" ]; then
        emit "INFO" "MemPalace" "No MemPalace config found, skipping index check"
        return
    fi

    emit "INFO" "MemPalace" "Checking $found_config for safe indexing..."

    if grep -qE '^\s*paths?:\s*\.' "$REPO_ROOT/$found_config" 2>/dev/null; then
        emit "HIGH" "MemPalace" "Config uses broad '.' indexing, may index runtime state" "$found_config"
    fi

    local excluded_dirs=".evol/ .xdd/ .git/ dialog/ tool_result/ memory/raw/"
    for excl in $excluded_dirs; do
        if grep -qE "(exclude|ignore|skip).*['\"]?${excl}" "$REPO_ROOT/$found_config" 2>/dev/null; then
            emit "OK" "MemPalace" "Config excludes $excl" "$found_config"
        fi
    done

    if grep -qF '.evol/' "$REPO_ROOT/$found_config" && ! grep -qE "exclude|ignore" "$REPO_ROOT/$found_config" 2>/dev/null; then
        emit "HIGH" "MemPalace" "Config references .evol/ without exclusion" "$found_config"
    fi
}

check_entrypoints() {
    emit "INFO" "Entrypoints" "Checking entrypoints if installed..."

    if ! command -v python3 >/dev/null 2>&1; then
        emit "INFO" "Entrypoints" "python3 not available, skipping"
        return
    fi

    if [ ! -f "$REPO_ROOT/pyproject.toml" ]; then
        emit "INFO" "Entrypoints" "pyproject.toml not found, skipping"
        return
    fi

    local entrypoints="evol evol-gate evol-eval evol-flow evol-provider evol-shield evol-orchestrate evol-agent evol-evolve evol-research evol-memory evol-lessons"
    for cmd in $entrypoints; do
        if command -v "$cmd" >/dev/null 2>&1; then
            emit "OK" "Entrypoints" "$cmd found in PATH" "$cmd"
        else
            emit "MEDIUM" "Entrypoints" "$cmd not in PATH (may need install)" "$cmd"
        fi
    done
}

check_manifest() {
    local manifest_file="$REPO_ROOT/agent.yaml"
    emit "INFO" "Manifest" "Checking agent.yaml..."

    if [ ! -f "$manifest_file" ]; then
        emit "MEDIUM" "Manifest" "agent.yaml not found (optional but recommended)" "$manifest_file"
        return
    fi

    local schema_file="$REPO_ROOT/schemas/agent-manifest.schema.json"
    if [ ! -f "$schema_file" ]; then
        emit "MEDIUM" "Manifest" "Schema not found: schemas/agent-manifest.schema.json" "$schema_file"
        return
    fi

    if command -v python3 >/dev/null 2>&1; then
        local result
        result=$(python3 -c "
import json, sys, yaml

try:
    import jsonschema
    with open('$schema_file') as f:
        schema = json.load(f)
    with open('$manifest_file') as f:
        manifest = yaml.safe_load(f)
    jsonschema.validate(manifest, schema)
    print('VALID')
except ImportError:
    print('NO_JSONSCHEMA')
except Exception as e:
    print(f'INVALID: {e}')
" 2>/dev/null) || result="SKIP"

        case "$result" in
            VALID)
                emit "OK" "Manifest" "agent.yaml validates against schema"
                local name version trigger
                name=$(python3 -c "import yaml; m=yaml.safe_load(open('$manifest_file')); print(m.get('name',''))" 2>/dev/null || echo "")
                version=$(python3 -c "import yaml; m=yaml.safe_load(open('$manifest_file')); print(m.get('version',''))" 2>/dev/null || echo "")
                trigger=$(python3 -c "import yaml; m=yaml.safe_load(open('$manifest_file')); print(m.get('canonical_trigger',''))" 2>/dev/null || echo "")
                if [ -n "$name" ] && [ -n "$version" ] && [ -n "$trigger" ]; then
                    emit "OK" "Manifest" "framework: $name v$version, trigger: $trigger"
                fi
                ;;
            NO_JSONSCHEMA)
                emit "LOW" "Manifest" "jsonschema not installed, skipping schema validation"
                ;;
            INVALID:*)
                emit "HIGH" "Manifest" "$result" "$manifest_file"
                ;;
            *)
                emit "MEDIUM" "Manifest" "Could not validate manifest"
                ;;
        esac
    else
        emit "LOW" "Manifest" "python3 not available for manifest validation"
    fi
}

check_dependencies() {
    emit "INFO" "Dependencies" "Checking critical dependencies..."

    if command -v git >/dev/null 2>&1; then
        emit "OK" "Dependencies" "git $(git --version | cut -d' ' -f3)"
    else
        emit "CRITICAL" "Dependencies" "git not found"
    fi

    if command -v python3 >/dev/null 2>&1; then
        local py_ver
        py_ver=$(python3 --version | cut -d' ' -f2)
        local py_major py_minor
        py_major=$(echo "$py_ver" | cut -d. -f1)
        py_minor=$(echo "$py_ver" | cut -d. -f2)
        if [ "$py_major" -eq 3 ] && [ "$py_minor" -ge 10 ]; then
            emit "OK" "Dependencies" "python3 $py_ver (>=3.10)"
        else
            emit "HIGH" "Dependencies" "python3 $py_ver requires 3.10+"
        fi
    else
        emit "CRITICAL" "Dependencies" "python3 not found"
    fi

    if command -v mempalace >/dev/null 2>&1; then
        emit "OK" "Dependencies" "mempalace CLI detected"
    else
        emit "LOW" "Dependencies" "mempalace not in PATH (optional)"
    fi
}

check_legacy_artifacts() {
    emit "INFO" "LegacyArtifacts" "Checking for deprecated xdd-* artifacts..."

    local legacy=(
        "xdd.profile.yml"
        ".xdd/"
        "scripts/xdd-doctor.sh"
        "scripts/xdd-init.sh"
        "scripts/xdd-gate.py"
    )

    for artifact in "${legacy[@]}"; do
        if [ -e "$REPO_ROOT/$artifact" ]; then
            emit "MEDIUM" "LegacyArtifacts" "Deprecated artifact found: $artifact" "$artifact"
        fi
    done

    if [ -d "$REPO_ROOT/.xdd" ] || [ -f "$REPO_ROOT/xdd.profile.yml" ]; then
        emit "MEDIUM" "LegacyArtifacts" "xdd-* paths found ( Evol-DD uses evol-* naming)"
    fi
}

print_summary() {
    if [ "$MODE_JSON" = true ]; then
        printf '{"status":"%s","exit_code":%d}\n' \
            $([ $EXIT_CODE -eq 0 ] && echo "PASS" || echo "FAIL") \
            $EXIT_CODE
    else
        echo ""
        echo "=== Doctor Complete ==="
        if [ $EXIT_CODE -eq 0 ]; then
            echo -e "${GREEN}[PASS]${NC} All critical checks passed"
        else
            echo -e "${RED}[FAIL]${NC} Critical or high issues detected"
        fi
    fi
}

main() {
    if [ "${1:-}" = "--json" ]; then
        MODE_JSON=true
    fi

    echo "=== Evol-DD Doctor v${EVOL_VERSION} ==="

    check_profile
    check_manifest
    check_required_files
    check_scripts_executable
    check_sensitive_permissions
    check_source_dirs_tracked
    check_mempalace_safe
    check_entrypoints
    check_dependencies
    check_legacy_artifacts

    print_summary
    exit $EXIT_CODE
}

main "$@"