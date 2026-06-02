#!/usr/bin/env python3
"""Evol-DD Gate Keeper — HMAC-SHA256 approval system."""
import os, sys, hmac, hashlib, json, argparse, base64
from datetime import datetime
from _evol_common import get_logger, get_data_dir, save_json, load_json

logger = get_logger("gate")

GATE_KEY_PATH = ".evol/.gate-key"
GATE_LOG_PATH = ".evol/.gate-log.jsonl"

def get_gate_key():
    """Get project-local gate key. Create if missing."""
    key_file = os.path.join(get_data_dir(), GATE_KEY_PATH)
    if not os.path.exists(key_file):
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        key = os.urandom(32)
        with open(key_file, "wb") as f:
            f.write(key)
        os.chmod(key_file, 0o600)
    with open(key_file, "rb") as f:
        return f.read()

def sign(message):
    key = get_gate_key()
    sig = hmac.new(key, message.encode(), hashlib.sha256).digest()
    return base64.b64encode(sig).decode()

def verify(message, signature):
    expected = sign(message)
    return hmac.compare_digest(expected, signature)

def approve(phase, approver="system"):
    """Record approval in log."""
    os.makedirs(os.path.dirname(os.path.join(get_data_dir(), GATE_LOG_PATH)), exist_ok=True)
    log_file = os.path.join(get_data_dir(), GATE_LOG_PATH)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "phase": phase,
        "approver": approver,
        "signature": sign(f"{phase}:{approver}:{datetime.now().isoformat()}")
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def init_gate():
    """Initialize gate for project."""
    key = get_gate_key()
    log_file = os.path.join(get_data_dir(), GATE_LOG_PATH)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "w") as f:
        f.write("")
    logger.info("Gate initialized at %s", os.path.join(get_data_dir(), GATE_KEY_PATH))

def status():
    """Show gate status."""
    log_file = os.path.join(get_data_dir(), GATE_LOG_PATH)
    if not os.path.exists(log_file):
        return []
    entries = []
    with open(log_file) as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

def main():
    parser = argparse.ArgumentParser(description="Evol-DD Gate Keeper")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("init", help="Initialize gate")
    sub.add_parser("status", help="Show gate log")
    
    p = sub.add_parser("approve", help="Record approval")
    p.add_argument("--phase", required=True, help="Phase name (e.g. briefing, spec, plan)")
    p.add_argument("--approver", default="human", help="Approver name")
    
    p = sub.add_parser("validate", help="Validate gate is initialized")
    
    p = sub.add_parser("transition", help="Record phase transition")
    p.add_argument("--from", dest="from_phase", required=True)
    p.add_argument("--to", dest="to_phase", required=True)
    
    args = parser.parse_args()
    
    if args.cmd == "init":
        init_gate()
        print("Gate initialized")
    elif args.cmd == "status":
        for e in status():
            print(f"[{e['timestamp']}] {e['phase']} approved by {e['approver']}")
    elif args.cmd == "approve":
        entry = approve(args.phase, args.approver)
        print(f"APROBADO: {args.phase} by {args.approver}")
    elif args.cmd == "validate":
        log_file = os.path.join(get_data_dir(), GATE_LOG_PATH)
        if os.path.exists(log_file):
            print("Gate active")
        else:
            print("Gate not initialized. Run: evol-gate init")
            sys.exit(1)
    elif args.cmd == "transition":
        entry = approve(f"{args.from_phase} -> {args.to_phase}", "system")
        print(f"Transition: {args.from_phase} -> {args.to_phase}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
