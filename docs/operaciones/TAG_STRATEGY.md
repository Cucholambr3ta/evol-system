# Tag Strategy

## Tag Format

All tags follow `v<MAJOR>.<MINOR>.<PATCH>` (semver).

Examples: `v0.1.0`, `v1.0.0`, `v2.3.1-beta`

## When to Tag

- **Release tags** (`vX.Y.Z`): created only after all CI gates pass, from `main`.
- **Pre-release tags** (`vX.Y.Z-alpha`, `vX.Y.Z-beta`): optional, from `release/*` branches.
- **Hotfix tags**: same format, from `main` after hotfix merge.

## No Tag Without Gates

The release checklist must be fully executed before any tag is created.
Gates are:
1. `pytest tests/`
2. `python3 scripts/validate-registry.py --strict`
3. `bash scripts/evol-doctor.sh`
4. `python3 scripts/evol-shield.py audit --ci --no-write`
5. `python3 scripts/evol-eval.py validate --all`
6. `python3 scripts/evol-eval.py run --all`

If any gate fails, no tag is created.

## Tag Annotation

Tags must be annotated with the changelog section:

```bash
git tag -a v0.1.0 -m "Release v0.1.0

## Added
- ...

## Changed
- ...

## Fixed
- ..."
```

## Tag Lifecycle

- Tags are permanent and immutable. Never retag.
- If a broken tag is pushed, create a new tag with incremented patch.
- Never delete tags from remote.

## CI Enforcement

CI checks for tags only on `main`. Any tag created outside the release process is rejected.
The release script verifies all gates before creating the tag.

## Signed Tags

Recommended: `git tag -s` for GPG-signed tags.

## Referencing Tags in Code

Use `VERSION` file as single source. Scripts read from it, never hardcode version strings.