# Contributing to Evol-DD

Thank you for your interest in contributing to Evol-DD.

## Development Workflow

We use GitFlow with `main` and `develop` branches.

1. **Branch from `develop`**: All feature and fix branches start from `develop`.
   ```bash
   git checkout develop
   git checkout -b feature/my-feature
   ```

2. **Conventional Commits**: All commits must follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation only
   - `chore:` maintenance
   - `refactor:` code refactoring
   - `test:` adding or updating tests
   - `perf:` performance improvements

3. **Branching convention**:
   - Features: `feature/<name>`
   - Fixes: `fix/<number>-<description>`
   - Releases: `release/vX.Y.Z`
   - Hotfixes: `hotfix/<name>`

4. **Commit and push your branch**:
   ```bash
   git add .
   git commit -m "feat(profile): add profile validation"
   git push -u origin feature/my-feature
   ```

5. **Open a Pull Request** to `develop`. PRs require:
   - Title following Conventional Commits
   - Description explaining what and why
   - CI passing (tests, lint, security)
   - No `|| true` masks or suppressed failures

6. **Merge**: Squash and merge or merge commit to `develop`. Delete branch after merge.

## Scripts and Entry Points

- `scripts/evol-init.sh` — Initialize new projects
- `scripts/evol-doctor.sh` — Diagnostics (exit non-zero on CRITICAL/HIGH)
- `scripts/evol-gate.py` — HMAC approval gate
- `scripts/evol-eval.py` — Eval harness
- `scripts/evol-shield.py` — Security audit

## Testing

```bash
pytest tests/
bats tests/*.bats
python3 scripts/validate-registry.py --strict
bash scripts/lint-workflows.sh
python3 scripts/evol-shield.py audit --ci --no-write
bash scripts/evol-doctor.sh
```

## Documentation Standard

All documentation must follow `docs/DOC_STANDARD.md`:
- Zero emojis
- Mermaid diagrams mandatory
- Tables for structured data
- Gherkin for acceptance criteria
- Trazabilidad bidireccional with REQ-NNN IDs

## Security

- Never commit secrets, keys or credentials
- `.evol/.gate-key` must be `0600`
- Report security issues via SECURITY.md process

## Questions

Open an issue for discussion before large PRs.