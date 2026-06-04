#!/usr/bin/env python3
"""Evol-DD Gate Keeper — HMAC-SHA256 chain-integrity approval system."""
import os, sys, hmac, hashlib, json, argparse, base64
from datetime import datetime, timezone
from _evol_common import get_logger, get_data_dir

logger = get_logger("gate")

GATE_KEY_PATH = ".evol/.gate-key"
GATE_LOG_PATH = ".evol/.gate-log.jsonl"
GATE_DIR = ".evol"

PAYLOAD_KEYS = ["timestamp", "phase", "approver", "action", "nonce", "previous_hash"]
GENESIS_HASH = "0" * 64

def _get_gate_dir():
    base = get_data_dir()
    return os.path.join(base, GATE_DIR)

def get_gate_key():
    """Get project-local gate key. Create if missing."""
    gate_dir = _get_gate_dir()
    key_file = os.path.join(gate_dir, ".gate-key")
    if not os.path.exists(key_file):
        os.makedirs(gate_dir, exist_ok=True)
        os.chmod(gate_dir, 0o700)
        key = os.urandom(32)
        with open(key_file, "wb") as f:
            f.write(key)
        os.chmod(key_file, 0o600)
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

def _enforce_grill_before_plan(phase):
    """Enforced pre-gate: el plan no se firma sin haber corrido /evol grill-me.

    Verifica que exista .evol/.grill-done-plan y que su SHA coincida con PLAN.md
    actual (interrogar un plan viejo no vale para un plan editado despues).

    Escape hatch documentado: EVOL_SKIP_GRILL=1 omite el check (registra warning).
    El check solo aplica a fases que firman/transicionan hacia/desde 'plan'.
    """
    phase_l = str(phase).lower()
    if "plan" not in phase_l:
        return  # solo aplica al gate del plan
    if os.environ.get("EVOL_SKIP_GRILL") == "1":
        logger.warning("EVOL_SKIP_GRILL=1 — gate del plan firmado SIN grill-me (override explicito)")
        return

    project = get_data_dir()
    plan_path = os.path.join(project, "PLAN.md")
    marker = os.path.join(project, ".evol", ".grill-done-plan")

    if not os.path.exists(plan_path):
        return  # sin PLAN.md no hay nada que interrogar (fase aun no produjo artefacto)

    if not os.path.exists(marker):
        print("BLOQUEADO: el gate del plan requiere /evol grill-me antes de firmar.", file=sys.stderr)
        print("  PLAN.md no ha sido interrogado. Correr: /evol grill-me", file=sys.stderr)
        print("  Override explicito (no recomendado): EVOL_SKIP_GRILL=1", file=sys.stderr)
        sys.exit(1)

    # Verificar que el grill corresponde al PLAN.md actual (no a una version vieja)
    with open(plan_path, "rb") as f:
        plan_sha = hashlib.sha256(f.read()).hexdigest()
    marker_sha = open(marker).read().strip()
    if marker_sha != plan_sha:
        print("BLOQUEADO: PLAN.md cambio despues del ultimo grill-me.", file=sys.stderr)
        print(f"  Interrogado: {marker_sha[:16]}... | Actual: {plan_sha[:16]}...", file=sys.stderr)
        print("  Re-interrogar el plan actualizado: /evol grill-me", file=sys.stderr)
        sys.exit(1)


# Orden inmutable de fases del pipeline (Constitucion Art. 9).
PHASE_ORDER = ["briefing", "spec", "plan", "build", "qa", "retro"]


def _approved_phases():
    """Devuelve el set de fases con accion 'approved' en el log (cadena valida)."""
    log_file = os.path.join(get_data_dir(), GATE_LOG_PATH)
    approved = set()
    if not os.path.exists(log_file):
        return approved
    with open(log_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            p = entry.get("payload", {})
            if p.get("action") == "approved":
                approved.add(str(p.get("phase", "")).lower())
    return approved


def _enforce_phase_chain(phase):
    """FSM: una fase no se firma sin que TODAS las previas esten 'approved' en el log.

    Solo aplica a fases del PHASE_ORDER. Escape hatch: EVOL_SKIP_CHAIN=1.
    """
    phase_l = str(phase).lower()
    if phase_l not in PHASE_ORDER:
        return  # fase libre (transiciones u otras), no se encadena
    if os.environ.get("EVOL_SKIP_CHAIN") == "1":
        logger.warning("EVOL_SKIP_CHAIN=1 — cadena de fases previas OMITIDA (override)")
        return
    idx = PHASE_ORDER.index(phase_l)
    approved = _approved_phases()
    missing = [p for p in PHASE_ORDER[:idx] if p not in approved]
    if missing:
        print(f"BLOQUEADO: no se puede firmar '{phase_l}' — fases previas sin aprobar:",
              file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        print("  Override explicito: EVOL_SKIP_CHAIN=1", file=sys.stderr)
        sys.exit(1)


def _enforce_segregation(phase, approver):
    """Separacion autor != aprobador. Si existe .evol/.author-<phase> y == approver, bloquea.

    Escape hatch: EVOL_SKIP_SEGREGATION=1.
    """
    author_file = os.path.join(get_data_dir(), ".evol", f".author-{phase}")
    if not os.path.exists(author_file):
        return  # sin autor registrado, no se compara
    author = open(author_file).read().strip()
    if author and author == approver:
        if os.environ.get("EVOL_SKIP_SEGREGATION") == "1":
            logger.warning(f"EVOL_SKIP_SEGREGATION=1 — autor==aprobador ({approver}) permitido (override)")
            return
        print(f"BLOQUEADO: aprobador '{approver}' es el autor del artefacto de '{phase}'.",
              file=sys.stderr)
        print("  Separacion de privilegios: el aprobador no puede ser el autor.", file=sys.stderr)
        print("  Override explicito: EVOL_SKIP_SEGREGATION=1", file=sys.stderr)
        sys.exit(1)


def set_author(phase, author):
    """Registra el autor del artefacto de una fase (.evol/.author-<phase>)."""
    gate_dir = _get_gate_dir()
    os.makedirs(gate_dir, exist_ok=True)
    author_file = os.path.join(get_data_dir(), ".evol", f".author-{phase}")
    with open(author_file, "w") as f:
        f.write(author)
    os.chmod(author_file, 0o600)
    print(f"[gate] autor de {phase}: {author}")


def approve(phase, approver="human", action="approved"):
    """Record approval in log with chain integrity."""
    _enforce_grill_before_plan(phase)
    _enforce_phase_chain(phase)
    _enforce_segregation(phase, approver)
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
    os.chmod(gate_dir, 0o700)
    log_file = os.path.join(gate_dir, ".gate-log.jsonl")
    with open(log_file, "w") as f:
        f.write("")
    os.chmod(log_file, 0o600)
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

def grill_done():
    """Marca que /evol grill-me interrogo el PLAN.md actual (libera el gate del plan).

    Escribe .evol/.grill-done-plan con el SHA-256 del PLAN.md. El gate del plan
    verifica este marker. Invocado por el workflow grill-me al completar el
    interrogatorio del plan.
    """
    project = get_data_dir()
    plan_path = os.path.join(project, "PLAN.md")
    if not os.path.exists(plan_path):
        print("ERROR: no existe PLAN.md para marcar como interrogado", file=sys.stderr)
        sys.exit(1)
    gate_dir = _get_gate_dir()
    os.makedirs(gate_dir, exist_ok=True)
    with open(plan_path, "rb") as f:
        plan_sha = hashlib.sha256(f.read()).hexdigest()
    marker = os.path.join(gate_dir, ".grill-done-plan")
    with open(marker, "w") as f:
        f.write(plan_sha)
    os.chmod(marker, 0o600)
    print(f"grill-me registrado para PLAN.md ({plan_sha[:16]}...). Gate del plan liberado.")

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

    sub.add_parser("grill-done", help="Marca PLAN.md como interrogado por grill-me (libera gate del plan)")

    p = sub.add_parser("set-author", help="Registra el autor del artefacto de una fase")
    p.add_argument("--phase", required=True, help="Phase name")
    p.add_argument("--author", required=True, help="Author name")

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
    elif args.cmd == "grill-done":
        grill_done()
    elif args.cmd == "set-author":
        set_author(args.phase, args.author)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()