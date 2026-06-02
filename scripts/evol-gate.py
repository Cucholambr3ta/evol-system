#!/usr/bin/env python3
"""Evol-DD Gate Keeper — HMAC-SHA256 chain-integrity approval system."""
import os, sys, hmac, hashlib, json, argparse, base64, stat
from datetime import datetime, timezone
from _evol_common import get_logger, get_data_dir

logger = get_logger("gate")

GATE_KEY_PATH = ".evol/.gate-key"
GATE_LOG_PATH = ".evol/.gate-log.jsonl"
GATE_DIR = ".evol"

PAYLOAD_KEYS = ["timestamp", "phase", "approver", "action", "nonce", "previous_hash"]
GENESIS_HASH = "0" * 64

def _secure_path(path, mode):
    """Set file permissions securely."""
    os.chmod(path, mode)

def _get_gate_dir():
    base = get_data_dir()
    return os.path.join(base, GATE_DIR)

def get_gate_key():
    """Get project-local gate key. Create if missing."""
    gate_dir = _get_gate_dir()
    key_file = os.path.join(gate_dir, ".gate-key")
    if not os.path.exists(key_file):
        os.makedirs(gate_dir, exist_ok=True)
        key = os.urandom(32)
        with open(key_file, "wb") as f:
            f.write(key)
        _secure_path(key_file, 0o600)
        _secure_path(gate_dir, 0o700)
    with open(key_file, "rb") as f:
        return f.read()

def _canonical_payload(phase, approver, action, nonce, previous_hash):
    """Build canonical JSON payload with ordered keys."""
    return json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "approver": approver,
        "action": action,
        "nonce": nonce,
        "previous_hash": previous_hash
    }, separators=(",", ":"))

def sign(message):
    key = get_gate_key()
    sig = hmac.new(key, message.encode(), hashlib.sha256).digest()
    return base64.b64encode(sig).decode()

def verify(message, signature):
    expected = sign(message)
    return hmac.compare_digest(expected, signature)

def _get_last_hash():
    """Get hash of last log entry for chain integrity."""
    log_file = os.path.join(get_data_dir(), GATE_LOG_PATH)
    if not os.path.exists(log_file):
        return GENESIS_HASH
    entries = []
    with open(log_file) as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    if not entries:
        return GENESIS_HASH
    return entries[-1]["payload_hash"]

def approve(phase, approver="human", action="approved"):
    """Record approval in log with chain integrity."""
    gate_dir = _get_gate_dir()
    os.makedirs(gate_dir, exist_ok=True)
    log_file = os.path.join(gate_dir, ".gate-log.jsonl")
    nonce = base64.b64encode(os.urandom(16)).decode()
    previous_hash = _get_last_hash()
    payload = _canonical_payload(phase, approver, action, nonce, previous_hash)
    signature = sign(payload)
    entry = {
        "payload": json.loads(payload),
        "signature": signature,
        "payload_hash": hashlib.sha256(payload.encode()).hexdigest()
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")
    os.chmod(log_file, 0o600)
    return entry

def _verify_entry(entry):
    """Verify a single log entry. Returns (valid, error_message)."""
    if "payload" not in entry or "signature" not in entry:
        return False, "missing payload or signature"
    try:
        payload_str = json.dumps(entry["payload"], separators=(",", ":"))
    except Exception:
        return False, "invalid payload JSON"
    if not verify(payload_str, entry["signature"]):
        return False, "signature mismatch"
    return True, ""

def _verify_chain():
    """Verify entire log chain. Returns (valid, errors)."""
    log_file = os.path.join(get_data_dir(), GATE_LOG_PATH)
    if not os.path.exists(log_file):
        return False, ["log file missing"]
    entries = []
    try:
        with open(log_file) as f:
            for i, line in enumerate(f):
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        return False, [f"line {i+1}: invalid JSON — {e}"]
    except IOError as e:
        return False, [f"read error — {e}"]
    if not entries:
        return False, ["log empty"]
    expected_prev = GENESIS_HASH
    errors = []
    for i, entry in enumerate(entries):
        valid, err = _verify_entry(entry)
        if not valid:
            errors.append(f"entry {i}: {err}")
        if entry["payload"].get("previous_hash") != expected_prev:
            errors.append(f"entry {i}: chain broken (expected {expected_prev[:16]}...)")
        expected_prev = entry["payload_hash"]
    if errors:
        return False, errors
    return True, []

def init_gate():
    """Initialize gate for project."""
    gate_dir = _get_gate_dir()
    os.makedirs(gate_dir, exist_ok=True)
    _secure_path(gate_dir, 0o700)
    log_file = os.path.join(gate_dir, ".gate-log.jsonl")
    with open(log_file, "w") as f:
        f.write("")
    _secure_path(log_file, 0o600)
    key = get_gate_key()
    logger.info("Gate initialized at %s", os.path.join(gate_dir, ".gate-key"))

def status(strict=False):
    """Show gate status. If strict, exit non-zero on invalid signatures."""
    log_file = os.path.join(get_data_dir(), GATE_LOG_PATH)
    if not os.path.exists(log_file):
        print("Gate: not initialized")
        return []
    entries = []
    with open(log_file) as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    print("ERROR: corrupted log entry")
                    sys.exit(1)
    for e in entries:
        valid, err = _verify_entry(e)
        status_icon = "OK" if valid else "INVALID"
        if not valid and strict:
            print(f"[{e.get('payload',{}).get('timestamp','?')}] {status_icon}: {err}")
            sys.exit(1)
        p = e.get("payload", {})
        print(f"[{p.get('timestamp','?')}] {p.get('phase','?')} ({p.get('action','?')}) by {p.get('approver','?')} [{status_icon}]")
    if strict:
        valid, errors = _verify_chain()
        if not valid:
            print("CHAIN BROKEN:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
    return entries

def validate(strict=True):
    """Validate gate. strict=True fails closed on any anomaly."""
    gate_dir = _get_gate_dir()
    key_file = os.path.join(gate_dir, ".gate-key")
    log_file = os.path.join(gate_dir, ".gate-log.jsonl")
    if not os.path.exists(key_file):
        print("FAIL: .gate-key missing")
        sys.exit(1)
    if not os.path.exists(log_file):
        print("FAIL: .gate-log.jsonl missing")
        sys.exit(1)
    key_mode = os.stat(key_file).st_mode & 0o777
    if key_mode != 0o600:
        print(f"FAIL: .gate-key permissions {oct(key_mode)}, expected 0600")
        sys.exit(1)
    valid, errors = _verify_chain()
    if not valid:
        print("SIGNATURE VALIDATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    print("Gate: VALID")
    sys.exit(0)

def transition(from_phase, to_phase, approver="system"):
    """Record phase transition."""
    phase = f"{from_phase} -> {to_phase}"
    entry = approve(phase, approver, "transition")
    print(f"Transition: {phase}")
    return entry

def main():
    parser = argparse.ArgumentParser(description="Evol-DD Gate Keeper")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init", help="Initialize gate")

    p = sub.add_parser("status", help="Show gate log")
    p.add_argument("--strict", action="store_true", help="Exit non-zero on invalid signatures")

    p = sub.add_parser("approve", help="Record approval")
    p.add_argument("--phase", required=True, help="Phase name")
    p.add_argument("--approver", default="human", help="Approver name")

    p = sub.add_parser("validate", help="Validate gate chain integrity")
    p.add_argument("--strict", action="store_true", default=True, help="Fail closed (default)")

    p = sub.add_parser("transition", help="Record phase transition")
    p.add_argument("--from", dest="from_phase", required=True)
    p.add_argument("--to", dest="to_phase", required=True)
    p.add_argument("--approver", default="system", help="Approver name")

    args = parser.parse_args()

    if args.cmd == "init":
        init_gate()
        print("Gate initialized")
    elif args.cmd == "status":
        status(strict=args.strict)
    elif args.cmd == "approve":
        entry = approve(args.phase, args.approver)
        print(f"APROBADO: {args.phase} by {args.approver}")
    elif args.cmd == "validate":
        validate(strict=getattr(args, "strict", True))
    elif args.cmd == "transition":
        entry = transition(args.from_phase, args.to_phase, getattr(args, "approver", "system"))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()