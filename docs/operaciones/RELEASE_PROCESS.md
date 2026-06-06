# Release Process

## Version Single Source of Truth

The canonical version source is `VERSION` at the repo root.

All scripts, CLI helpers, and docs read from `VERSION`. The `pyproject.toml` version
field is updated at release time via `scripts/bump-version.py`.

**Rule: Never edit version strings manually in any file except `VERSION`.**

## GitFlow Branches

- `main`: production-ready, only merges from `release/*`
- `develop`: integration branch, always contains latest dev
- `feature/*`: new features
- `fix/*`: bug fixes
- `release/*`: release preparation, created from `develop`
- `hotfix/*`: urgent production fixes, created from `main`

## Tag Strategy

Tags follow `v<MAJOR>.<MINOR>.<PATCH>` format (e.g., `v0.1.0`).

**No tag is created before all gates pass.**

Tag annotation must include the changelog section for that version.

**Rule: Every release MUST include explicit Upgrade Notes in the tag and CHANGELOG, detailing any manual steps required or if `evol update apply` covers the upgrade entirely.**

## Release Checklist

```bash
# 1. Verify develop is clean
git checkout develop && git pull

# 2. Run all gates
pytest tests/
python3 scripts/validate-registry.py --strict
bash scripts/evol-doctor.sh
python3 scripts/evol-shield.py audit --ci --no-write
python3 scripts/evol-eval.py validate --all
python3 scripts/evol-eval.py run --all

# 3. Create release branch
git checkout -b release/0.1.0 develop

# 4. Bump version
python3 scripts/bump-version.py 0.1.0  # writes to pyproject.toml and VERSION

# 5. Update CHANGELOG.md — move [Unreleased] to [0.1.0] with today's date

# 6. Commit release prep
git add -A && git commit -m "release: prepare v0.1.0"

# 7. Merge to main
git checkout main && git merge release/0.1.0 --no-ff -m "release: merge v0.1.0"

# 8. Create tag
git tag -a v0.1.0 -m "Release v0.1.0

## Upgrade Notes
- ...

## Added
- ...

## Changed
- ...

## Fixed
- ..."

# 9. Merge to develop
git checkout develop && git merge release/0.1.0 --no-ff

# 10. Delete release branch
git branch -d release/0.1.0

# 11. Push everything
git push origin main develop && git push origin v0.1.0
```

## Version Bump Script

`scripts/bump-version.py` accepts one argument: the new version string.
It updates:
- `VERSION`
- `pyproject.toml` version field

## No Tag Without Gates

CI must be green before any tag is created. The release checklist enforces this.
If a gate fails, do not create the release branch. Fix the issue first.

## Hotfix Process

```bash
git checkout main
git pull
git checkout -b hotfix/<description>
# fix and commit with conventional commit
git checkout main && git merge hotfix/<description> --no-ff
git tag v<patch>
git checkout develop && git merge hotfix/<description> --no-ff
git branch -d hotfix/<description>
git push origin main develop v<patch>
```

---

## Como los consumidores del framework se actualizan

Una vez publicada la nueva version en PyPI o disponible en el repo fuente, los
proyectos que usan Evol-DD actualizan con un solo comando:

```bash
# Desde el directorio del proyecto consumidor
evol update check     # verificar si hay nueva version
evol update apply     # aplicar: upgrade paquete + propagar workflows + regenerar IDE
```

`evol update apply` hace en secuencia:

1. Actualiza el paquete: `pipx upgrade evol-dd` (o `pip install --upgrade evol-dd`)
2. Propaga workflows SSoT actualizados: copia `.agent/workflows/*.md` al proyecto
3. Propaga templates actualizados: copia `templates/*.md` y `templates/*.yml`
4. Regenera configs IDE: ejecuta `evol-adapt.sh all --dest=<proyecto>`

Para modo legacy (sin pip):

```bash
export EVOL_SOURCE_DIR=/ruta/al/repo/evol-dd  # apuntar a la nueva version
evol update apply --project /tu-proyecto
```

**Invariante post-release:** despues de publicar, verificar que `evol --version`
en una instalacion limpia de pipx muestra la version correcta (no `0.1.0-dev`
stale). Esto confirma que el empaquetado incluye el `VERSION` file correcto.