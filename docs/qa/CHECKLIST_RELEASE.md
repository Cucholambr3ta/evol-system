# Checklist Release — Evol-DD

## Pre-Release Gates

### 1. Tests

```bash
pytest tests/ -v
bats tests/*.bats
```

Salida esperada: todos los tests passando, exit code 0.

### 2. Registry y Equipo

```bash
python3 scripts/validate-registry.py --strict
bash scripts/generate-equipo.sh
git diff docs/equipo.md  # verificar sincronizado
```

### 3. Linting

```bash
bash scripts/lint-workflows.sh
```

### 4. Security

```bash
python3 scripts/evol-shield.py audit --ci --no-write
gitleaks detect --source .
```

### 5. Packaging

```bash
python3 -m pip install -e .[dev]
evol --version
evol-gate --help
evol-eval --help
```

### 6. Bootstrap

```bash
tmpdir=$(mktemp -d)
bash scripts/evol-init.sh "$tmpdir" --profile=full
bash "$tmpdir/scripts/evol-doctor.sh"
rm -rf "$tmpdir"
```

### 7. Idempotencia

```bash
bats tests/test_init_idempotent.bats
```

### 8. Anti-MCP / Anti-Emoji

```bash
grep -r "mcpServers" . --include="*.yml" --include="*.json" --include="*.md" 2>/dev/null | grep -v ".git/" | wc -l  # debe ser 0
grep -rE "[\x{1F300}-\x{1F9FF}]" docs/ --include="*.md" 2>/dev/null | wc -l  # debe ser 0
```

### 9. Evals

```bash
python3 scripts/evol-eval.py validate --all
python3 scripts/evol-eval.py run --all
```

## Cut Release

### Version

```bash
cat VERSION  # Fuente unica de verdad
# Si hay incremento:
# 1. Editar VERSION
# 2. Editar pyproject.toml version
# 3. Editar evol.config.yml evol_version
# 4. git add + commit + tag
```

### Changelog

Verificar que `CHANGELOG.md` existe y sigue Conventional Commits.
Mover items de `[Unreleased]` a `[<version>] - YYYY-MM-DD`.

```bash
git add CHANGELOG.md && git commit -m "docs(changelog): release v<version>"
```

### GitFlow

```bash
# 1. develop -> release/X.Y.Z
git checkout develop && git pull
git checkout -b release/0.2.0 develop
git add -A && git commit -m "release: prepare v0.2.0"

# 2. Merge a main
git checkout main && git pull
git merge release/0.2.0 --no-ff -m "release: merge v0.2.0"
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin main --tags

# 3. Merge main -> develop
git checkout develop && git pull
git merge release/0.2.0 --no-ff
git push origin develop

# 4. Limpiar
git branch -d release/0.2.0
```

## Post-Release

- [ ] CI en main passa
- [ ] Tag visible en GitHub
- [ ] CHANGELOG.md completo en main
- [ ] Documentacion actualizada si corresponde

## Rollback

Si gates fallan despues del tag:

- NO borrar el tag
- Crear hotfix: `git checkout -b hotfix/<desc> main`
- Fix y repetir release process
- O revertir merge commit y re-tag si es catastrophico

## Comandos Rapidos

```bash
set -e
pytest tests/
bats tests/*.bats
python3 scripts/validate-registry.py --strict
bash scripts/lint-workflows.sh
python3 scripts/evol-shield.py audit --ci --no-write
python3 scripts/evol-eval.py validate --all
```
