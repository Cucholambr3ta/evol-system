#!/usr/bin/env bash
# evol-gitflow.sh — GitFlow automatizado por sprint para proyectos Evol-DD.
#
# Subcomandos:
#   setup   --mode=dev|collab [--remote=URL]
#   sprint-start --sprint=NN --title=<titulo> [--type=feature|fix]
#   sprint-close --sprint=NN
#   pre-push
#   status
#
# Variables de entorno:
#   EVOL_GITFLOW_MODE=dev|collab    Override de modo
#   EVOL_SKIP_PREPUSH=1             Salta checks pre-push
#   EVOL_SKIP_GITLEAKS=1            Salta gitleaks

set -euo pipefail

VERSION="1.0.0"
EVOL_DIR="$(pwd)/.evol"
GITFLOW_STATE="${EVOL_DIR}/gitflow.mode"

# ── helpers ───────────────────────────────────────────────────────────────────

log()  { echo "[evol-gitflow] $*"; }
warn() { echo "[evol-gitflow] WARN: $*" >&2; }
err()  { echo "[evol-gitflow] ERROR: $*" >&2; exit 1; }

EVOL_GITIGNORE_PATTERNS=(
  "acuerdos/"
  "memoria.md"
  "lecciones.md"
  ".evol/"
  "evol.profile.yml"
  "AGENT_MEMORY.md"
  "memory/"
  "dialog/"
  "tool_result/"
)

sprint_num() { printf "%02d" "$1"; }

get_mode() {
  if [ -n "${EVOL_GITFLOW_MODE:-}" ]; then echo "$EVOL_GITFLOW_MODE"; return; fi
  if [ -f "$GITFLOW_STATE" ]; then cat "$GITFLOW_STATE"; else echo "dev"; fi
}

save_mode() {
  mkdir -p "$EVOL_DIR"
  echo "$1" > "$GITFLOW_STATE"
  chmod 600 "$GITFLOW_STATE"
}

ensure_git() {
  git rev-parse --git-dir >/dev/null 2>&1 || err "No es un repositorio git. Ejecutar desde la raiz del proyecto."
}

current_branch() { git rev-parse --abbrev-ref HEAD; }

# ── setup ─────────────────────────────────────────────────────────────────────

EVOL_DIR_REMOTE_STATE="$(pwd)/.evol/gitflow.remote"

_save_remote_mode() {
  mkdir -p "$(dirname "$EVOL_DIR_REMOTE_STATE")"
  echo "$1" > "$EVOL_DIR_REMOTE_STATE"
  chmod 600 "$EVOL_DIR_REMOTE_STATE"
}

_get_remote_mode() {
  [ -f "$EVOL_DIR_REMOTE_STATE" ] && cat "$EVOL_DIR_REMOTE_STATE" || echo "remote"
}

_create_remote_repo() {
  local name="$1" visibility="$2"
  command -v gh >/dev/null 2>&1 || err "gh CLI no instalado. Instalar: https://cli.github.com/ o usar --remote=URL"
  gh auth status >/dev/null 2>&1 || err "gh no autenticado. Correr: gh auth login"
  [ -z "$name" ] && name="$(basename "$(pwd)")"
  log "Creando repo GitHub: $name ($visibility)..."
  if gh repo create "$name" --"$visibility" --source=. --remote=origin 2>/dev/null; then
    log "Repo creado y origin configurado: $(git remote get-url origin 2>/dev/null || echo '?')"
  else
    err "gh repo create fallo. Verificar que '$name' no exista ya."
  fi
}

cmd_setup() {
  local mode="dev" remote="" create=0 local_only=0 repo_name="" visibility="private"
  while [ $# -gt 0 ]; do
    case "$1" in
      --mode=*) mode="${1#*=}"; shift ;;
      --remote=*) remote="${1#*=}"; shift ;;
      --create) create=1; shift ;;
      --local) local_only=1; shift ;;
      --name=*) repo_name="${1#*=}"; shift ;;
      --visibility=*) visibility="${1#*=}"; shift ;;
      *) err "Argumento desconocido: $1" ;;
    esac
  done
  [ "$mode" = "dev" ] || [ "$mode" = "collab" ] || err "Modo invalido: $mode. Usar dev o collab."
  [ "$visibility" = "private" ] || [ "$visibility" = "public" ] || err "Visibility invalida: private o public."
  ensure_git

  log "Configurando GitFlow modo=$mode"

  if ! git rev-parse --verify main >/dev/null 2>&1; then
    if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
      git checkout -b main
      git commit --allow-empty -m "chore: init repo"
    else
      git checkout -b main 2>/dev/null || git checkout main
    fi
  fi

  if ! git rev-parse --verify develop >/dev/null 2>&1; then
    git checkout main
    git checkout -b develop
    log "Branch develop creada."
  fi

  if [ "$local_only" = "1" ]; then
    _save_remote_mode "local"
    log "Modo local-only: sin remoto. No se hara push."
  elif [ "$create" = "1" ]; then
    _create_remote_repo "$repo_name" "$visibility"
    _save_remote_mode "remote"
  elif [ -n "$remote" ]; then
    if git remote get-url origin >/dev/null 2>&1; then
      git remote set-url origin "$remote"
    else
      git remote add origin "$remote"
    fi
    log "Remote origin: $remote"
    _save_remote_mode "remote"
  fi

  save_mode "$mode"
  _ensure_gitignore
  git checkout develop 2>/dev/null || true

  log "GitFlow configurado: modo=$mode | branches: main + develop"
  [ "$mode" = "dev" ] && log "Dev-solo: PRs auto-mergeadas via gh cli." || log "Collab: PRs requieren reviewer."
}

# ── sprint-start ──────────────────────────────────────────────────────────────

cmd_sprint_start() {
  local sprint="" title="" type="feature"
  while [ $# -gt 0 ]; do
    case "$1" in
      --sprint=*) sprint="${1#*=}"; shift ;;
      --title=*) title="${1#*=}"; shift ;;
      --type=*) type="${1#*=}"; shift ;;
      *) err "Argumento desconocido: $1" ;;
    esac
  done
  [ -n "$sprint" ] || err "--sprint requerido"
  [ -n "$title" ] || err "--title requerido"
  [ "$type" = "feature" ] || [ "$type" = "fix" ] || err "--type debe ser feature o fix"
  ensure_git

  local snum branch_name
  snum=$(sprint_num "$sprint")
  branch_name="${type}/sprint-${snum}-${title}"

  git rev-parse --verify develop >/dev/null 2>&1 || err "Branch develop no existe. Ejecutar: evol-gitflow.sh setup"
  _check_previous_sprint_merged "$snum"

  git checkout develop
  git checkout -b "$branch_name"
  log "Branch creada: $branch_name"
}

# ── sprint-close ──────────────────────────────────────────────────────────────

cmd_sprint_close() {
  local sprint=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --sprint=*) sprint="${1#*=}"; shift ;;
      *) err "Argumento desconocido: $1" ;;
    esac
  done
  [ -n "$sprint" ] || err "--sprint requerido"
  ensure_git

  local snum current
  snum=$(sprint_num "$sprint")
  current=$(current_branch)

  cmd_pre_push

  # Actualizar memoria del sprint
  if command -v python3 >/dev/null 2>&1; then
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python3 "${script_dir}/evol-memory.py" --project="$(pwd)" sprint-close --sprint="$sprint" 2>/dev/null || true

    log "Sincronizando sidecars JSON de documentacion..."
    python3 "${script_dir}/evol-doc-sync.py" sync-folder docs/ 2>/dev/null || true
    python3 "${script_dir}/evol-doc-sync.py" sync-folder acuerdos/ 2>/dev/null || true

    if git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -q "registry\.json"; then
      log "Cambios detectados en registry.json. Regenerando equipo.md..."
      bash "${script_dir}/generate-equipo.sh" 2>/dev/null || true
    fi
  fi

  git push -u origin "$current" 2>/dev/null || warn "No se pudo hacer push a origin."

  local mode
  mode=$(get_mode)
  if command -v gh >/dev/null 2>&1 && git remote get-url origin >/dev/null 2>&1; then
    _create_pr "$current" "$snum" "$mode"
  else
    log "gh cli no disponible. PR manual requerida."
  fi
  log "Sprint $snum cerrado."
}

# ── release-close ──────────────────────────────────────────────────────────────────
# Punto de integracion entre el flujo de Release y la Memoria Persistente.
# Debe invocarse ANTES del tag git en todo release: evol-gitflow.sh release-close --version=X.Y.Z

cmd_release_close() {
  local version=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --version=*) version="${1#*=}"; shift ;;
      *) err "Argumento desconocido: $1" ;;
    esac
  done
  [ -n "$version" ] || err "--version requerido (ej: --version=0.5.0)"
  ensure_git

  log "Release-close v${version}: actualizando memoria persistente..."

  if command -v python3 >/dev/null 2>&1; then
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # 1. Generar atomos de sprint con el numero de version como identificador
    python3 "${script_dir}/evol-memory.py" --project="$(pwd)" \
      sprint-close --sprint="release-${version}" 2>/dev/null || true

    # 2. Sincronizar el agregado MEMORY.md
    python3 "${script_dir}/evol-memory.py" --project="$(pwd)" \
      memory-split 2>/dev/null || true

    # 3. Sincronizar sidecars JSON de documentacion
    log "Sincronizando sidecars JSON de documentacion..."
    python3 "${script_dir}/evol-doc-sync.py" sync-folder docs/ 2>/dev/null || true
    python3 "${script_dir}/evol-doc-sync.py" sync-folder acuerdos/ 2>/dev/null || true

    # 4. Regenerar equipo.md
    log "Regenerando equipo.md..."
    bash "${script_dir}/generate-equipo.sh" 2>/dev/null || true

    log "Memoria y documentacion actualizadas: acuerdos/memoria/, MEMORY.md y sidecars sincronizados."
  else
    warn "python3 no disponible. Actualizar memoria manualmente con /update-memory."
  fi

  log "Release-close v${version}: OK. Proceder con: git tag -a v${version} -m 'Release v${version}'"
}

_create_pr() {
  local branch="$1" snum="$2" mode="$3"
  local title="Sprint ${snum}: $(echo "$branch" | sed 's|.*/sprint-[0-9]*-||')"
  local body="## Sprint ${snum}

Cierre automatico via evol-gitflow.sh.

### Checklist
- [ ] Tests verdes
- [ ] Shield 0 CRITICAL
- [ ] Lecciones en acuerdos/lecciones/sprint-${snum}.md

🤖 Generated with Evol-DD evol-gitflow.sh"

  if [ "$mode" = "dev" ]; then
    gh pr create --title "$title" --body "$body" --base develop --head "$branch" 2>/dev/null && \
      gh pr merge --squash --auto "$branch" 2>/dev/null && log "PR creada y marcada auto-merge." || \
      log "PR ya existe o sin auto-merge disponible."
  else
    gh pr create --title "$title" --body "$body" --base develop --head "$branch" 2>/dev/null && \
      log "PR creada (collab — requiere reviewer)." || log "PR ya existe."
  fi
}

# ── pre-push ──────────────────────────────────────────────────────────────────

cmd_pre_push() {
  if [ "${EVOL_SKIP_PREPUSH:-0}" = "1" ]; then
    warn "EVOL_SKIP_PREPUSH=1 — checks omitidos."
    return 0
  fi
  ensure_git
  log "Ejecutando checks pre-push..."
  _ensure_gitignore
  _check_evol_artifacts_not_staged
  _check_readme_status

  if [ "${EVOL_SKIP_GITLEAKS:-0}" != "1" ]; then
    if command -v gitleaks >/dev/null 2>&1; then
      gitleaks detect --no-banner --exit-code 1 2>/dev/null && log "gitleaks: limpio." || \
        err "gitleaks: secretos detectados. Resolver antes de push."
    else
      warn "gitleaks no instalado. Saltar con EVOL_SKIP_GITLEAKS=1."
    fi
  fi
  log "Pre-push: OK."
}

_ensure_gitignore() {
  local gitignore=".gitignore" modified=0
  [ -f "$gitignore" ] || touch "$gitignore"
  for pattern in "${EVOL_GITIGNORE_PATTERNS[@]}"; do
    if ! grep -qxF "$pattern" "$gitignore" 2>/dev/null; then
      echo "$pattern" >> "$gitignore"
      log "  .gitignore += $pattern"
      modified=1
    fi
  done
  [ "$modified" = "1" ] && log ".gitignore actualizado con patrones Evol-DD." || true
}

_check_evol_artifacts_not_staged() {
  local staged violations=()
  staged=$(git diff --cached --name-only 2>/dev/null || true)
  for pattern in "${EVOL_GITIGNORE_PATTERNS[@]}"; do
    local clean="${pattern%/}"
    while IFS= read -r file; do
      echo "$file" | grep -q "^${clean}" && violations+=("$file") || true
    done <<< "$staged"
  done
  if [ ${#violations[@]} -gt 0 ]; then
    warn "Artefactos Evol-DD en staging (no deben ir al repo del producto):"
    for v in "${violations[@]}"; do warn "  - $v"; done
    err "Pre-push bloqueado por artefactos Evol-DD en staging."
  fi
}

_check_readme_status() {
  local base_branch="develop"
  git rev-parse --verify develop >/dev/null 2>&1 || base_branch="main"
  if git diff --name-only "$base_branch"...HEAD 2>/dev/null | grep -i -q "README\.md$"; then
    log "Archivos README.md actualizados en esta rama."
  else
    warn "Ningun README.md modificado. Recomendacion: Ejecuta '/evol readme-master' para mantener estandar Top 100 en el proyecto."
  fi
}

_check_previous_sprint_merged() {
  local current_snum="$1"
  [ "$current_snum" = "01" ] && return 0
  local prev_snum
  prev_snum=$(printf "%02d" $((10#$current_snum - 1)))
  local prev_branches
  prev_branches=$(git branch --list "*sprint-${prev_snum}*" 2>/dev/null || true)
  [ -z "$prev_branches" ] && return 0
  for branch in $prev_branches; do
    branch="${branch// /}"; branch="${branch#\* }"
    git merge-base --is-ancestor "$branch" develop 2>/dev/null || \
      err "Branch '$branch' (sprint-${prev_snum}) no mergeada en develop. Completar sprint anterior primero."
  done
}

# ── status ────────────────────────────────────────────────────────────────────

cmd_status() {
  ensure_git
  local mode current
  mode=$(get_mode); current=$(current_branch)
  echo "[evol-gitflow] Estado GitFlow"
  echo "  Modo:          $mode"
  echo "  Branch actual: $current"
  echo "  Branches de sprint:"
  git branch --list "*sprint-*" | sed 's/^/    /'
  echo "  .gitignore Evol-DD:"
  for pattern in "${EVOL_GITIGNORE_PATTERNS[@]}"; do
    grep -qxF "$pattern" .gitignore 2>/dev/null && echo "    ✓ $pattern" || echo "    ✗ $pattern (faltante)"
  done
}

# ── main ──────────────────────────────────────────────────────────────────────

show_usage() {
  cat <<EOF
evol-gitflow.sh v${VERSION} — GitFlow automatizado para proyectos Evol-DD

Uso: evol-gitflow.sh <subcomando> [opciones]

Subcomandos:
  setup          --mode=dev|collab [--remote=URL]
  sprint-start   --sprint=NN --title=<titulo> [--type=feature|fix]
  sprint-close   --sprint=NN
  release-close  --version=X.Y.Z   (actualiza memoria antes del tag)
  pre-push
  status
  --version

Variables de entorno:
  EVOL_GITFLOW_MODE=dev|collab
  EVOL_SKIP_PREPUSH=1
  EVOL_SKIP_GITLEAKS=1
EOF
}

case "${1:-}" in
  setup)          shift; cmd_setup "$@" ;;
  sprint-start)   shift; cmd_sprint_start "$@" ;;
  sprint-close)   shift; cmd_sprint_close "$@" ;;
  release-close)  shift; cmd_release_close "$@" ;;
  pre-push)       shift; cmd_pre_push "$@" ;;
  status)         shift; cmd_status "$@" ;;
  --version|-v)   echo "evol-gitflow.sh v${VERSION}" ;;
  --help|-h|"")   show_usage ;;
  *) err "Subcomando desconocido: $1. Ver: evol-gitflow.sh --help" ;;
esac
