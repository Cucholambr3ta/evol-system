#!/usr/bin/env bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

apply_brand() {
    local brand_name="${1:-Evol-DD}"
    local brand_color="${2:-#7C3AED}"
    local brand_tagline="${3:-El framework que evoluciona.}"

    echo "[brand] Applying: $brand_name ($brand_color)"
    echo "[brand] Tagline: $brand_tagline"

    sed -i "s/Evol-DD/$brand_name/g; s/#7C3AED/$brand_color/g" "$REPO_ROOT/AGENTS.md" 2>/dev/null || true
    sed -i "s/El framework que evoluciona./$brand_tagline/g" "$REPO_ROOT/AGENTS.md" 2>/dev/null || true

    mkdir -p "$REPO_ROOT/.claude"
    cat > "$REPO_ROOT/.claude/branding.json" << EOF
{
  "name": "$brand_name",
  "color": "$brand_color",
  "tagline": "$brand_tagline",
  "trigger": "evol"
}
EOF

    echo "[brand] Done"
}

if [ -f "$REPO_ROOT/evol.profile.yml" ]; then
    brand=$(grep "^  name:" "$REPO_ROOT/evol.profile.yml" | cut -d: -f2 | tr -d ' "')
    color=$(grep "^  color:" "$REPO_ROOT/evol.profile.yml" | cut -d: -f2 | tr -d ' "')
    tagline=$(grep "^  tagline:" "$REPO_ROOT/evol.profile.yml" | cut -d: -f2 | tr -d ' "')
    apply_brand "$brand" "$color" "$tagline"
else
    apply_brand
fi