#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

validate_color() {
    if ! [[ "$1" =~ ^#[0-9A-Fa-f]{6}$ ]]; then
        echo "ERROR: color must be valid hex format (#RRGGBB): $1" >&2
        exit 1
    fi
}

validate_traversal() {
    if [[ "$1" =~ \.\. ]]; then
        echo "ERROR: $2 contains path traversal attempt: $1" >&2
        exit 1
    fi
}

write_brand_json() {
    python3 -c "
import json, sys
name = sys.argv[1]
color = sys.argv[2]
tagline = sys.argv[3]
output = sys.argv[4]
obj = {'name': name, 'color': color, 'tagline': tagline, 'trigger': 'evol'}
with open(output, 'w') as f:
    json.dump(obj, f, ensure_ascii=False, indent=2)
    f.write('\n')
" "$1" "$2" "$3" "$4"
}

apply_brand() {
    local brand_name="${1:-Evol-DD}"
    local brand_color="${2:-#7C3AED}"
    local brand_tagline="${3:-El framework que evoluciona.}"

    validate_traversal "$brand_name" "name"
    validate_traversal "$brand_tagline" "tagline"
    validate_color "$brand_color"

    echo "[brand] Applying: $brand_name ($brand_color)"
    echo "[brand] Tagline: $brand_tagline"

    mkdir -p "$REPO_ROOT/.claude"
    write_brand_json "$brand_name" "$brand_color" "$brand_tagline" "$REPO_ROOT/.claude/branding.json"

    echo "[brand] Done"
}

if [ -f "$REPO_ROOT/evol.profile.yml" ]; then
    tmp_result=$(mktemp)
    python3 << PYEOF
import sys, yaml, json

profile_path = '$REPO_ROOT/evol.profile.yml'
result_path = '$tmp_result'

try:
    with open(profile_path) as f:
        data = yaml.safe_load(f)
    branding = data.get('brand', {})
    name = branding.get('name', 'Evol-DD')
    color = branding.get('color', '#7C3AED')
    tagline = branding.get('tagline', 'El framework que evoluciona.')
    obj = {'name': name, 'color': color, 'tagline': tagline}
    with open(result_path, 'w') as f:
        json.dump(obj, f)
except yaml.YAMLError as e:
    with open(result_path, 'w') as f:
        f.write('ERROR:' + str(e))
    sys.exit(0)
except Exception as e:
    with open(result_path, 'w') as f:
        f.write('ERROR:' + str(e))
    sys.exit(0)
PYEOF

    if grep -q "^ERROR:" "$tmp_result" 2>/dev/null; then
        echo "ERROR: Invalid YAML in evol.profile.yml" >&2
        grep "^ERROR:" "$tmp_result" | cut -c6- >&2
        rm -f "$tmp_result"
        exit 1
    fi
    brand_name=$(python3 -c "import json; print(json.load(open('$tmp_result'))['name'])")
    brand_color=$(python3 -c "import json; print(json.load(open('$tmp_result'))['color'])")
    brand_tagline=$(python3 -c "import json; print(json.load(open('$tmp_result'))['tagline'])")
    rm -f "$tmp_result"
    apply_brand "$brand_name" "$brand_color" "$brand_tagline"
else
    apply_brand
fi