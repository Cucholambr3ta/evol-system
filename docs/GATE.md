# GATE — HMAC Chain Integrity Protocol

## Overview

The gate is an approval system using HMAC-SHA256 signatures with a tamper-evident chain. Every approval entry is signed and chained via `previous_hash`, enabling detection of log tampering.

## Architecture

```
.evol/
  .gate-key        # HMAC-SHA256 key, 0600 permissions
  .gate-log.jsonl  # Signed chain entries, 0600 permissions
```

## Payload Schema

Every gate entry contains a signed payload with these canonical fields (ordered):

```json
{
  "timestamp": "2026-06-02T12:00:00+00:00",
  "phase": "briefing",
  "approver": "human",
  "action": "approved",
  "nonce": "base64_random_16_bytes",
  "previous_hash": "sha256_of_previous_entry"
}
```

The payload is serialized as canonical JSON (`separators=(",",":")`) before signing.

## Chain Integrity

Entries are chained via `previous_hash`:

- Entry 0: `previous_hash = "0" * 64` (genesis)
- Entry N: `previous_hash = sha256(entry N-1)` where entry includes `payload_hash`

`payload_hash` is the SHA-256 of the canonical payload JSON string.

## Signing

Signature = `base64(HMAC-SHA256(key, canonical_payload_json))`

Verification uses `hmac.compare_digest` to prevent timing attacks.

## Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize gate (creates key + empty log) |
| `approve --phase <name> [--approver <name>]` | Record approval |
| `validate [--strict]` | Verify chain (fail-closed by default) |
| `status [--strict]` | Show log with integrity check |
| `transition --from <phase> --to <phase>` | Record phase transition |

## Permissions

| File | Mode | Rationale |
|------|------|-----------|
| `.evol/` | 0700 | Private runtime directory |
| `.evol/.gate-key` | 0600 | Secrets only readable by owner |
| `.evol/.gate-log.jsonl` | 0600 | Sensitive audit log |

## Fail-Closed Behavior

`validate` and `status --strict` exit with code 1 when:

- Key file missing
- Log file missing
- Log empty (requires at least one entry)
- Any entry fails signature verification
- Chain `previous_hash` does not match expected value

## Security Properties

- **Tamper detection**: Modifying any payload invalidates its signature
- **Chain integrity**: Deleting/reordering entries breaks the `previous_hash` chain
- **Timing safety**: Uses `hmac.compare_digest` for signature comparison
- **Nonce**: Each entry includes a random nonce to prevent replay (optional enforcement)

## Negative Test Coverage

- Log tampering: payload modified → signature mismatch detected
- Invalid signature: signature replaced → verification fails
- Key missing: `.gate-key` removed → validate fails
- Phase not approved: empty log → chain validation fails
- Log truncated: entry removed → chain broken (previous_hash mismatch)