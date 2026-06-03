#!/usr/bin/env bash
# evol-adapt.sh — Genera configs IDE desde .agent/workflows/ SSoT.
# Copia REAL (no symlinks). Sin MCP en ningun adapter.
set -eu

TRIGGER="${EVOL_TRIGGER:-evol}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKFLOWS_DIR="$REPO_ROOT/.agent/workflows"
DEST=""   # directorio destino del proyecto a adaptar (default: REPO_ROOT)

usage() {
    cat <<EOF
evol-adapt — Genera configs IDE desde el SSoT de Evol-DD.

Uso:
  bash scripts/evol-adapt.sh <target> [--dest=PATH] [--trigger=NAME] [--dry-run]

Targets:
  claude-code     .claude/commands/*.md (slash commands)
  opencode        .opencode/command/*.md + AGENTS.md
  cursor          .cursor/rules/<trigger>.mdc (@-mention)
  windsurf        .windsurf/workflows/*.md (slash nativos)
  vscode-copilot  .github/prompts/*.prompt.md
  antigravity     .agents/skills/<trigger>.md
  codex           ~/.codex/skills/<trigger>-orchestrator/
  all             todos los anteriores

Opciones:
  --dest=PATH     directorio del proyecto a adaptar (default: directorio actual)
  --trigger=NAME  trigger custom (default: evol)
  --dry-run       mostrar sin escribir
EOF
}

copy_workflows() {
    # copy_workflows <out_dir> <extension>
    local out_dir="$1" ext="$2"
    mkdir -p "$out_dir"
    local count=0
    for wf in "$WORKFLOWS_DIR"/*.md; do
        [ -f "$wf" ] || continue
        local name
        name=$(basename "$wf" .md)
        cp "$wf" "$out_dir/${name}.${ext}"
        count=$((count+1))
    done
    echo "[evol-adapt] $count archivos → $out_dir"
}

generate_claude_code() {
    local dest="${1:-$REPO_ROOT}"
    local out_dir="$dest/.claude/commands"
    echo "[claude-code] → $out_dir"
    copy_workflows "$out_dir" "md"
    # CLAUDE.md si no existe
    if [ ! -f "$dest/CLAUDE.md" ]; then
        cp "$REPO_ROOT/CLAUDE.md" "$dest/CLAUDE.md" 2>/dev/null || true
    fi
}

generate_opencode() {
    local dest="${1:-$REPO_ROOT}"
    local out_dir="$dest/.opencode/command"
    echo "[opencode] → $out_dir"
    mkdir -p "$dest/.opencode"
    copy_workflows "$out_dir" "md"
    # AGENTS.md para governance
    cp "$REPO_ROOT/AGENTS.md" "$dest/.opencode/AGENTS.md" 2>/dev/null || true
    # docs/equipo.md si existe
    if [ -d "$REPO_ROOT/prompts/agents" ] && command -v python3 >/dev/null 2>&1; then
        mkdir -p "$dest/docs"
        python3 "$REPO_ROOT/scripts/generate-equipo.sh" "$dest/docs/equipo.md" 2>/dev/null || true
    fi
}

generate_cursor() {
    local dest="${1:-$REPO_ROOT}"
    local out_dir="$dest/.cursor/rules"
    echo "[cursor] → $out_dir"
    mkdir -p "$out_dir"
    cat > "$out_dir/${TRIGGER}.mdc" <<EOF
---
description: Orquestador Evol-DD. Pipeline 6 fases. Activar con @${TRIGGER}.
globs:
alwaysApply: false
---
# /${TRIGGER} — Orquestador Evol-DD

Activar con @${TRIGGER}. Workflows en \`.agent/workflows/\`.
Lee \`memoria.md\` + \`lecciones.md\` + \`CLAUDE.md\` al iniciar (Constitucion Art. 3).
EOF
    echo "[evol-adapt] .cursor/rules/${TRIGGER}.mdc"
}

generate_windsurf() {
    local dest="${1:-$REPO_ROOT}"
    local out_dir="$dest/.windsurf/workflows"
    echo "[windsurf] → $out_dir"
    mkdir -p "$dest/.windsurf/rules"
    copy_workflows "$out_dir" "md"
    cat > "$dest/.windsurf/rules/${TRIGGER}.md" <<EOF
# /${TRIGGER} — Orquestador Evol-DD (Windsurf)

Activar con \`/${TRIGGER}\` (slash nativo) o @${TRIGGER}.
Pipeline 6 fases. Lee memoria/lecciones/CLAUDE al iniciar.
EOF
}

generate_vscode_copilot() {
    local dest="${1:-$REPO_ROOT}"
    local out_dir="$dest/.github/prompts"
    echo "[vscode-copilot] → $out_dir"
    copy_workflows "$out_dir" "prompt.md"
    # tasks.json si no existe
    if [ ! -f "$dest/.vscode/tasks.json" ]; then
        mkdir -p "$dest/.vscode"
        cat > "$dest/.vscode/tasks.json" <<EOF
{
  "version": "2.0.0",
  "tasks": [
    {"label": "Evol-DD: doctor","type": "shell","command": "evol doctor","problemMatcher": []},
    {"label": "Evol-DD: start","type": "shell","command": "evol start","problemMatcher": []},
    {"label": "Evol-DD: gate status","type": "shell","command": "evol gate status","problemMatcher": []}
  ]
}
EOF
    fi
}

generate_antigravity() {
    local dest="${1:-$REPO_ROOT}"
    local skills_src="$REPO_ROOT/skills"
    local out_dir="$dest/.agents/skills"
    echo "[antigravity] → $out_dir"
    if [ -d "$skills_src" ]; then
        mkdir -p "$out_dir"
        local count=0
        for sd in "$skills_src"/*/; do
            [ -d "$sd" ] || continue
            cp -r "$sd" "$out_dir/"
            count=$((count+1))
        done
        echo "[evol-adapt] $count skills → $out_dir"
    fi
    mkdir -p "$dest/.antigravity"
    cat > "$dest/.antigravity/README-evol.md" <<EOF
# Evol-DD en Antigravity

Skills en \`.agents/skills/\`. Activar con \`/${TRIGGER}\` o trigger de cada skill.
Re-sync: bash scripts/evol-adapt.sh antigravity --dest=<proyecto>
EOF
}

generate_codex() {
    local dest="${1:-$REPO_ROOT}"
    local codex_home="${EVOL_CODEX_HOME:-$HOME/.codex/skills}"
    local orch_dir="$codex_home/${TRIGGER}-orchestrator"
    echo "[codex] → $orch_dir"
    mkdir -p "$orch_dir/references" "$orch_dir/scripts"
    cat > "$orch_dir/SKILL.md" <<EOF
---
name: ${TRIGGER}-orchestrator
description: Use when the user starts with /${TRIGGER}, asks to coordinate Evol-DD pipeline (6 gated phases), select specialist agents, or invoke the Evol-DD orchestrator.
---

# Evol-DD Orchestrator (${TRIGGER})

Coordinate the Evol-DD pipeline: gated 6-phase development.

## Trigger
- \`/${TRIGGER} <objective>\` — invoke pipeline
- \`/${TRIGGER} validate <phase>\` — gate validation

## References
- \`references/agents-index.json\` — core agents
- \`references/workflows-index.md\` — available workflows
EOF
    # agents-index.json
    if [ -f "$REPO_ROOT/prompts/agents/registry.json" ] && command -v python3 >/dev/null 2>&1; then
        python3 - "$REPO_ROOT/prompts/agents/registry.json" "$orch_dir/references/agents-index.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
index = [{"id": a["id"], "name": a["name"].lower().replace(" ","-"),
          "category": a.get("category",""), "description": (a.get("description","") or "")[:200]}
         for a in data.get("agents", [])]
json.dump(index, open(sys.argv[2], "w", encoding="utf-8"), indent=2)
PY
    fi
    # workflows-index
    {
        echo "# Evol-DD Workflows"
        echo
        for wf in "$WORKFLOWS_DIR"/*.md; do
            local base; base=$(basename "$wf" .md)
            local desc
            desc=$(grep -m1 "^description:" "$wf" 2>/dev/null | sed 's/description:[[:space:]]*//' | tr -d '"'"'" | head -c 120)
            echo "- **${base}** — ${desc:-(sin descripcion)}"
        done
    } > "$orch_dir/references/workflows-index.md"
    # skills propias
    if [ -d "$REPO_ROOT/skills" ]; then
        local count=0
        for sd in "$REPO_ROOT/skills"/*/; do
            [ -d "$sd" ] || continue
            sname=$(basename "$sd")
            [ -d "$codex_home/$sname" ] && continue
            cp -r "$sd" "$codex_home/"
            count=$((count+1))
        done
        [ $count -gt 0 ] && echo "[evol-adapt] $count skills → $codex_home/"
    fi
    echo "[evol-adapt] Codex orchestrator: $orch_dir"
}

main() {
    local target="" dry_run=false

    while [ $# -gt 0 ]; do
        case "$1" in
            --dry-run) dry_run=true; shift ;;
            --trigger=*) TRIGGER="${1#*=}"; shift ;;
            --trigger) TRIGGER="$2"; shift 2 ;;
            --dest=*) DEST="${1#*=}"; shift ;;
            --dest) DEST="$2"; shift 2 ;;
            -h|--help) usage; exit 0 ;;
            -*) shift ;;
            *) target="$1"; shift ;;
        esac
    done

    # DEST default: directorio actual (proyecto del usuario), no el repo del framework
    DEST="${DEST:-$PWD}"
    if [ ! -d "$DEST" ]; then
        echo "[evol-adapt] ERROR: destino no existe: $DEST" >&2
        exit 1
    fi

    if [ -z "$target" ]; then
        usage; exit 1
    fi

    if [ "$dry_run" = true ]; then
        echo "[dry-run] target=$target dest=$DEST trigger=$TRIGGER"
        echo "  workflows: $(ls "$WORKFLOWS_DIR"/*.md 2>/dev/null | wc -l)"
        return
    fi

    echo "[evol-adapt] dest=$DEST trigger=/$TRIGGER"

    case "$target" in
        claude-code)    generate_claude_code    "$DEST" ;;
        opencode)       generate_opencode       "$DEST" ;;
        cursor)         generate_cursor         "$DEST" ;;
        windsurf)       generate_windsurf       "$DEST" ;;
        vscode-copilot) generate_vscode_copilot "$DEST" ;;
        antigravity)    generate_antigravity    "$DEST" ;;
        codex)          generate_codex          "$DEST" ;;
        all)
            generate_claude_code    "$DEST"
            generate_opencode       "$DEST"
            generate_cursor         "$DEST"
            generate_windsurf       "$DEST"
            generate_vscode_copilot "$DEST"
            generate_antigravity    "$DEST"
            generate_codex          "$DEST"
            echo ""
            echo "[all] Verificando 0 refs MCP..."
            grep -rn 'mcpServers\|evol-mcp-server' \
                "$DEST/.claude/" "$DEST/.opencode/" "$DEST/.cursor/" \
                "$DEST/.windsurf/" "$DEST/.agents/" \
                --include='*.md' --include='*.json' 2>/dev/null \
                || echo "[all] OK: 0 refs MCP"
            ;;
        *) echo "Target desconocido: $target"; usage; exit 1 ;;
    esac

    echo ""
    echo "[evol-adapt] Listo. target=$target dest=$DEST trigger=/${TRIGGER}"
}

main "$@"
