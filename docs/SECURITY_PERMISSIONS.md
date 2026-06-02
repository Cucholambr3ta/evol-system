# Permission Policy — Evol-DD

## Overview

This document defines the file-system permission policy for the Evol-DD framework.

## Policy by File Type

| Type | Path Examples | Mode | Rationale |
|------|-------------|------|-----------|
| Secrets | `.evol/.gate-key` | `0600` | HMAC key — owner-only |
| Sensitive logs | `.evol/.gate-log.jsonl` | `0600` or `0640` | Gate chain log — owner/group only |
| Runtime private dirs | `.evol/`, `memory/`, `dialog/`, `tool_result/` | `0700` or `0750` | Private runtime state |
| State database | `~/.evol/state.db` | Inherited from dir `0700` | SQLite with dir permissions |
| Source dirs | `scripts/`, `prompts/`, `src/`, `tests/`, etc. | `0755` | Readable for team, not group-writable |
| Scripts (executable) | `scripts/evol-*.sh`, `scripts/evol-*.py` | `0755` | Executable by owner/group/world |
| Hook scripts | `.agent/hooks/scripts/` | `0755` | Executable but not group-writable |
| Configs (non-secret) | `evol.profile.yml`, `pyproject.toml` | `0644` | Shared read |

## Enforcement

- **evol-doctor.sh**: Checks permissions on `.evol/.gate-key`, `.evol/.gate-log.jsonl`, `.evol/`, `memory/`, `dialog/`, `tool_result/`, `.agent/hooks/scripts/`. Fails HIGH on wrong permissions for secrets.
- **evol-shield.py**: Detects group-writable files in sensitive paths via `check_permissions()`.
- **evol-gate.py**: Sets `0600` on key/log, `0700` on `.evol/` at creation time.
- **evol-state.py**: Sets `0700` on state db parent directory at creation.

## Group-Writable Risk

Group-writable files and directories are a security risk in multi-user systems. An attacker with group membership can:
1. Read `.gate-key` and forge gate approvals.
2. Modify `.gate-log.jsonl` to backdate approvals.
3. Overwrite scripts to inject arbitrary code.

The policy prohibits group-writable (`g+w`) bits on sensitive paths.

## Creating Sensitive Runtime Files

```bash
mkdir -p .evol
chmod 0700 .evol

# Secret key
openssl rand -base64 32 > .evol/.gate-key
chmod 0600 .evol/.gate-key

# Log
touch .evol/.gate-log.jsonl
chmod 0600 .evol/.gate-log.jsonl
```

## Python Reference

```python
import os

def create_secure_file(path, data, mode=0o600):
    with open(path, "w") as f:
        f.write(data)
    os.chmod(path, mode)

def create_secure_dir(path, mode=0o700):
    os.makedirs(path, exist_ok=True)
    os.chmod(path, mode)
```

## CI/Gates

Any `doctor` or `shield --ci` run that detects group-writable sensitive files must fail.