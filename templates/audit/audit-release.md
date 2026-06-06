# Audit Template — Release
# Extiende audit-base.md con checks especificos del flujo de release.
# Invocar: evol-gitflow.sh release-close --version=X.Y.Z

## HEREDA: templates/audit/audit-base.md
## (Ejecutar primero el checklist universal antes de este)

---

## Checklist Especifico — Fase: Release

### F. Pre-flight de Release

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| F1 | `pytest tests/ -v` paso al 100% | `[ ]` | Exit code 0 |
| F2 | `validate-registry.py --strict` sin errores | `[ ]` | 17 core agents OK |
| F3 | `evol-shield.py audit --ci --no-write` con 0 violations | `[ ]` | |
| F4 | `evol-eval.py validate --all` OK | `[ ]` | |
| F5 | `gitleaks detect` sin secretos | `[ ]` | |

### G. Versionamiento

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| G1 | `VERSION` actualizado al nuevo semver | `[ ]` | Fuente unica de verdad |
| G2 | `pyproject.toml version` sincronizado con `VERSION` | `[ ]` | |
| G3 | `evol.config.yml evol_version` actualizado | `[ ]` | Si existe el campo |
| G4 | Bump semver correcto segun commits | `[ ]` | feat=minor, fix=patch, BREAKING=major |

### H. CHANGELOG y Comunicacion

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| H1 | `CHANGELOG.md` tiene seccion `[X.Y.Z] - YYYY-MM-DD` | `[ ]` | Keep a Changelog |
| H2 | Items agrupados: Added, Changed, Fixed, Removed | `[ ]` | |
| H3 | `[Unreleased]` vacio post-release | `[ ]` | |

### I. GitFlow del Release

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| I1 | Release branch `release/X.Y.Z` creada desde `develop` | `[ ]` | |
| I2 | Merge a `main` con `--no-ff` | `[ ]` | Sin fast-forward |
| I3 | Tag `vX.Y.Z` creado en `main` | `[ ]` | `git tag -a vX.Y.Z` |
| I4 | Merge de `release/X.Y.Z` de vuelta a `develop` | `[ ]` | Bidireccional |
| I5 | Rama `release/X.Y.Z` eliminada post-merge | `[ ]` | |
| I6 | `git push origin main --tags` ejecutado | `[ ]` | |
| I7 | `git push origin develop` ejecutado | `[ ]` | |

### J. Memoria (gate obligatorio pre-tag)

| # | Item | Veredicto | Descripcion |
|---|------|-----------|-------------|
| J1 | `evol-gitflow.sh release-close --version=X.Y.Z` ejecutado | `[ ]` | ANTES del tag |
| J2 | `acuerdos/memoria/decisiones.md` refleja decisiones del release | `[ ]` | |
| J3 | `acuerdos/memoria/convenciones.md` actualizado | `[ ]` | |
| J4 | `acuerdos/memoria/riesgos.md` con mitigados/nuevos | `[ ]` | |
| J5 | `MEMORY.md` regenerado via `memory-split` | `[ ]` | |

---

## Puntos Ciegos Especificos — Release

1. **Commits sin firma GPG:** `git log --show-signature -5` — GitHub bloquea en ramas protegidas.
2. **Warnings de registry:** `validate-registry.py` reporta skills faltantes en agents? Anotar como SKILL_MISSING.
3. **src/evol_cli/ mirrors desincronizados:** Scripts/skills/workflows tienen copia en `src/`? Verificar `diff scripts/ src/evol_cli/scripts/`.
4. **README.md no actualizado:** `evol-gitflow.sh pre-push` advirtio sobre READMEs sin actualizar?
5. **Dependencias de PyPI desactualizadas:** `pip list --outdated` antes del release.

---

## Secuencia Correcta de Release (referencia)

```bash
# 1. Gate de memoria (NUEVO - obligatorio)
bash scripts/evol-gitflow.sh release-close --version=X.Y.Z

# 2. Bump de version
echo "X.Y.Z" > VERSION
# Editar pyproject.toml version = "X.Y.Z"

# 3. CHANGELOG
# Mover [Unreleased] a [X.Y.Z] - YYYY-MM-DD

# 4. Commit de preparacion
git add VERSION pyproject.toml CHANGELOG.md
git commit -m "release: prepare vX.Y.Z"

# 5. GitFlow
git checkout main && git merge release/X.Y.Z --no-ff -m "release: merge vX.Y.Z"
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git checkout develop && git merge release/X.Y.Z --no-ff
git branch -d release/X.Y.Z

# 6. Push
git push origin main --tags && git push origin develop
```
