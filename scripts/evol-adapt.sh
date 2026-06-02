#!/usr/bin/env bash
set -e

TRIGGER="${EVOL_TRIGGER:-evol}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKFLOWS_DIR="$REPO_ROOT/.agent/workflows"
EXPECTED_ROOT="$(realpath "$REPO_ROOT")"

TRIGGER_REGEX='^[A-Za-z0-9_-]+$'

usage() {
    echo "Usage: $0 <target> [--dry-run] [--trigger=<trigger>]"
    echo "  Targets: claude-code, opencode, cursor, windsurf, vscode-copilot, antigravity, codex, all"
    echo "  --dry-run    Show what would be generated"
    echo "  --trigger    Override trigger word (default: evol)"
}

sanitize_trigger() {
    local trigger="$1"
    if ! [[ "$trigger" =~ $TRIGGER_REGEX ]]; then
        echo "[ERROR] Invalid trigger: '$trigger' - must match $TRIGGER_REGEX" >&2
        exit 1
    fi
    if [[ "$trigger" == *..* ]] || [[ "$trigger" == */* ]]; then
        echo "[ERROR] Path traversal detected in trigger: '$trigger'" >&2
        exit 1
    fi
}

validate_output_path() {
    local out_dir="$1"
    local resolved
    resolved=$(realpath "$out_dir" 2>/dev/null || echo "$out_dir")
    local resolved_root
    resolved_root=$(realpath "$EXPECTED_ROOT" 2>/dev/null || echo "$EXPECTED_ROOT")
    if [[ "$resolved" != "$resolved_root"/* ]]; then
        if [[ "$resolved" != "${HOME}/.codex"* ]]; then
            echo "[ERROR] Output path '$resolved' outside allowed directory" >&2
            exit 1
        fi
    fi
}

check_no_overwrite() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        echo "[ERROR] Would overwrite existing file: $file_path" >&2
        echo "[ERROR] Remove existing file first or use a different trigger" >&2
        exit 1
    fi
}

check_file_exists() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        echo "[ERROR] File already exists: $file_path" >&2
        echo "[ERROR] Refusing to overwrite. Remove the file first." >&2
        exit 1
    fi
}

generate_claude_code() {
    local out_dir="$REPO_ROOT/.claude/commands"
    mkdir -p "$out_dir"
    echo "[claude-code] Generating..."
    for wf in "$WORKFLOWS_DIR"/*.md; do
        local name=$(basename "$wf" .md)
        local content=$(cat "$wf")
        cat > "$out_dir/${name}.md" <<< "$content"
    done
    echo "[claude-code] Done: $out_dir"
}

generate_opencode() {
    local out_dir="$REPO_ROOT/.opencode/command"
    mkdir -p "$out_dir"
    echo "[opencode] Generating..."
    for wf in "$WORKFLOWS_DIR"/*.md; do
        local name=$(basename "$wf" .md)
        local content=$(cat "$wf")
        cat > "$out_dir/${name}.md" <<< "$content"
    done
    if [ -f "$REPO_ROOT/AGENTS.md" ]; then
        cp "$REPO_ROOT/AGENTS.md" "$REPO_ROOT/.opencode/AGENTS.md"
    fi
    echo "[opencode] Done: $out_dir"
}

generate_cursor() {
    local out_dir="$REPO_ROOT/.cursor/rules"
    mkdir -p "$out_dir"
    echo "[cursor] Generating..."
    for wf in "$WORKFLOWS_DIR"/*.md; do
        local name=$(basename "$wf" .md)
        local content=$(cat "$wf")
        cat > "$out_dir/${name}.mdc" <<< "$content"
    done
    echo "[cursor] Done: $out_dir"
}

generate_windsurf() {
    local out_dir="$REPO_ROOT/.windsurf/workflows"
    mkdir -p "$out_dir"
    echo "[windsurf] Generating..."
    for wf in "$WORKFLOWS_DIR"/*.md; do
        local name=$(basename "$wf" .md)
        local content=$(cat "$wf")
        cat > "$out_dir/${name}.md" <<< "$content"
    done
    echo "[windsurf] Done: $out_dir"
}

generate_vscode_copilot() {
    local out_dir="$REPO_ROOT/.github/prompts"
    mkdir -p "$out_dir"
    echo "[vscode-copilot] Generating..."
    for wf in "$WORKFLOWS_DIR"/*.md; do
        local name=$(basename "$wf" .md)
        local content=$(cat "$wf")
        cat > "$out_dir/${name}.prompt.md" <<< "$content"
    done
    echo "[vscode-copilot] Done: $out_dir"
}

generate_antigravity() {
    local out_dir="$REPO_ROOT/.agents/skills"
    mkdir -p "$out_dir"
    echo "[antigravity] Generating..."
    for wf in "$WORKFLOWS_DIR"/*.md; do
        local name=$(basename "$wf" .md)
        local content=$(cat "$wf")
        cat > "$out_dir/${name}.md" <<< "$content"
    done
    echo "[antigravity] Done: $out_dir"
}

generate_codex() {
    local out_dir="${HOME}/.codex/skills/${TRIGGER}-orchestrator"
    validate_output_path "$out_dir"
    mkdir -p "$out_dir"
    echo "[codex] Generating to $out_dir..."
    for wf in "$WORKFLOWS_DIR"/*.md; do
        local name=$(basename "$wf" .md)
        local dest_file="$out_dir/${name}.md"
        check_file_exists "$dest_file"
        cat > "$dest_file" <<< "$content"
    done
    echo "[codex] Done: $out_dir"
}

main() {
    local target=""
    local dry_run=false

    while [ $# -gt 0 ]; do
        case "$1" in
            --dry-run) dry_run=true; shift ;;
            --trigger=*) TRIGGER="${1#*=}"; shift ;;
            -*) shift ;;
            *) target="$1"; shift ;;
        esac
    done

    sanitize_trigger "$TRIGGER"

    if [ -z "$target" ]; then
        usage; exit 1
    fi

    if [ "$dry_run" = true ]; then
        echo "[dry-run] Would generate for: $target"
        echo "  Workflows: $(ls "$WORKFLOWS_DIR"/*.md 2>/dev/null | wc -l)"
        return
    fi

    case "$target" in
        claude-code) generate_claude_code ;;
        opencode) generate_opencode ;;
        cursor) generate_cursor ;;
        windsurf) generate_windsurf ;;
        vscode-copilot) generate_vscode_copilot ;;
        antigravity) generate_antigravity ;;
        codex) generate_codex ;;
        all)
            generate_claude_code
            generate_opencode
            generate_cursor
            generate_windsurf
            generate_vscode_copilot
            generate_antigravity
            generate_codex
            echo ""
            echo "[all] Generation complete. Anti-MCP check:"
            grep -rn 'mcpServers\|mcp\.json\|evol-mcp-server' \
                .claude/ .opencode/ .cursor/ .windsurf/ .agents/ .antigravity/ \
                --include='*.md' --include='*.mdc' --include='*.json' 2>/dev/null \
                || echo "OK: 0 MCP references found"
            ;;
        *) echo "Unknown target: $target"; usage; exit 1 ;;
    esac

    echo "[evol-adapt] Complete"
}

main "$@"