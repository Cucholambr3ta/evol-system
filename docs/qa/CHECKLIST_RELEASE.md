# Release Checklist

## Pre-Release Gates (all must pass)

- [ ] `pytest tests/` passes
- [ ] `python3 scripts/validate-registry.py --strict` passes
- [ ] `bash scripts/evol-doctor.sh` exits 0
- [ ] `python3 scripts/evol-shield.py audit --ci --no-write` reports no CRITICAL
- [ ] `python3 scripts/evol-eval.py validate --all` passes
- [ ] `python3 scripts/evol-eval.py run --all` passes
- [ ] `bats tests/*.bats` passes (if bats installed)
- [ ] CI on develop is green

## Version

- [ ] Read current version from `VERSION` (single source of truth)
- [ ] Decide if bump is patch/minor/major per semver rules
- [ ] Run `python3 scripts/bump-version.py <new_version>` to update VERSION + pyproject.toml

## Changelog

- [ ] Verify `CHANGELOG.md` exists and follows Conventional Commits
- [ ] Move items from `[Unreleased]` to `[<version>] - YYYY-MM-DD`
- [ ] Add date for the release
- [ ] Commit: `git add CHANGELOG.md && git commit -m "docs(changelog): release v<version>"`

## Release Branch

- [ ] `git checkout develop && git pull`
- [ ] `git checkout -b release/<version> develop`
- [ ] Commit release prep: `git add -A && git commit -m "release: prepare v<version>"`

## Merge to Main

- [ ] `git checkout main && git pull`
- [ ] `git merge release/<version> --no-ff -m "release: merge v<version>"`
- [ ] Create signed tag: `git tag -a v<version> -m "Release v<version>"`
- [ ] Push main: `git push origin main`

## Merge to Develop

- [ ] `git checkout develop && git pull`
- [ ] `git merge release/<version> --no-ff`
- [ ] Push develop: `git push origin develop`
- [ ] Delete release branch: `git branch -d release/<version>`
- [ ] Push tag: `git push origin v<version>`

## Post-Release

- [ ] Verify CI on main is green
- [ ] Verify tag is visible in GitHub/GitLab
- [ ] Verify CHANGELOG.md on main is complete
- [ ] Update documentation if needed

## Rollback (if gates fail after tag)

- [ ] Do NOT delete the tag
- [ ] Create hotfix branch: `git checkout -b hotfix/<description> main`
- [ ] Fix issue and repeat release process
- [ ] Or revert the merge commit and re-tag if catastrophic