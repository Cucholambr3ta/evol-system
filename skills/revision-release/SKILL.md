---
name: revision-release
description: >
  Revisión completa del proyecto: analiza historial de GitHub desde el último release,
  identifica mejoras, verifica métodos de instalación (curl, pipx, npm) y arma el
  paquete instalador. Usar al preparar un release o cuando se pida una revisión
  integral del proyecto. Sinonimos: /revision-release, revisar release, preparar release.
origin: project
category: release
when_to_use:
  - Preparar un nuevo release
  - Revisar estado del proyecto antes de release
  - Verificar métodos de instalación
  - Identificar mejoras pendientes
triggers:
  - /revision-release
  - "revisar release"
  - "preparar release"
compatible_with:
  - claude-code
  - opencode
  - cursor
  - windsurf
  - vscode-copilot
  - antigravity
  - codex
---

# revision-release

## Proposito

Ejecutar una revisión completa del proyecto antes de un release:
1. Analizar historial de GitHub desde el último release
2. Identificar mejoras, bugs corregidos, features nuevas
3. Verificar métodos de instalación (curl, pipx, npm)
4. Generar CHANGELOG y paquete instalador
5. Verificar que todo esté listo para release

## Uso

```
/revision-release
```

## Protocolo

### 1. Detectar último release

```bash
# Último tag de release
git describe --tags --abbrev=0 2>/dev/null || echo "sin-releases"

# Último release en GitHub
gh release list --limit 1 2>/dev/null || echo "gh-no-disponible"
```

### 2. Analizar historial desde último release

```bash
# Commits desde último tag
git log $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD")..HEAD --oneline

# Archivos cambiados
git diff --stat $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD")..HEAD
```

### 3. Clasificar cambios

| Tipo | Descripción |
|------|-------------|
| Features | Nuevas funcionalidades |
| Fixes | Bugs corregidos |
| Breaking | Cambios breaking changes |
| Docs | Solo documentación |
| Refactor | Refactoring sin cambio funcional |
| Tests | Tests agregados/corregidos |

### 4. Verificar métodos de instalación

#### 4.1 curl | bash

```bash
# Verificar que install.sh existe y es funcional
cat install.sh | head -20
bash install.sh --dry-run
```

#### 4.2 pipx

```bash
# Verificar que pyproject.toml está correcto
python3 -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Verificar que el paquete builda
python3 -m build --sdist --no-isolation 2>/dev/null || echo "build-fallido"
```

#### 4.3 npm (si aplica)

```bash
# Verificar package.json si existe
cat package.json 2>/dev/null || echo "npm-no-configurado"
```

### 5. Generar artefactos de release

#### 5.1 CHANGELOG

```bash
# Generar CHANGELOG desde commits conventional
git log $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD")..HEAD \
  --pretty=format:"- %s (%h)" --no-merges
```

#### 5.2 Versionar

```bash
# Leer versión actual
cat VERSION

# Sugerir nueva versión (semver)
# Major: breaking changes
# Minor: new features
# Patch: fixes
```

### 6. Verificaciones previas

| Check | Comando | Esperado |
|-------|---------|----------|
| Tests pasan | `python3 -m pytest tests/ -q` | 0 failures |
| Lint OK | `python3 -m py_compile scripts/*.py` | Sin errores |
| CHANGELOG actualizado | `git diff CHANGELOG.md` | Cambios |
| VERSION actualizado | `git diff VERSION` | Cambios |
| install.sh funcional | `bash install.sh --dry-run` | OK |
| pyproject.toml válido | `python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"` | OK |

### 7. Generar resumen

```markdown
## Resumen de Release v<X.Y.Z>

### Features nuevas
- ...

### Bugs corregidos
- ...

### Breaking changes
- ...

### Métodos de instalación
- [x] curl | bash (install.sh)
- [x] pipx install evol-dd
- [ ] npm install (pendiente)

### Pendientes
- ...
```

## Output

La skill genera:
1. Resumen de cambios clasificados
2. Verificación de métodos de instalación
3. Sugerencia de versión semver
4. Artefactos listos para commit (CHANGELOG, VERSION)

## Notas

- Requiere `gh` CLI para historial de GitHub (fallback a git local)
- `npm` está pendiente de implementar (no hay package.json aún)
- `--dry-run` en install.sh para verificar sin instalar
