#!/usr/bin/env python3
"""evol-crash — Crash root-cause analysis nativo para X-DD.

Analiza crash logs y core dumps para determinar causa raiz.
Degrada elegantemente: usa gdb si disponible, heuristico si no.

Comandos:
  analyze <crash_log>              — analisis completo desde log
  hypothesis <crash_log>           — LLM genera hipotesis de causa raiz
  reproduce <crash_log> <binary>   — intenta reproducir (requiere gdb)
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

def _now(): return datetime.now(timezone.utc).isoformat()

def _load_provider():
    scripts = Path(__file__).parent
    for name in ("evol-provider.py", "evol-provider.py"):
        prov = scripts / name
        if prov.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("_prov", prov)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            provider_env = os.environ.get("EVOL_PROVIDER", os.environ.get("EVOL_PROVIDER", "mock"))
            if provider_env == "mock":
                return mod.MockProvider()
            try:
                return mod.AnthropicProvider()
            except Exception:
                return mod.MockProvider()
    return None

# ── Crash log parsing ─────────────────────────────────────────────────────────

SIGNAL_NAMES = {
    "11": "SIGSEGV (Segmentation fault — invalid memory access)",
    "6": "SIGABRT (Abort — assertion failed or explicit abort())",
    "8": "SIGFPE (Floating point exception — division by zero or overflow)",
    "4": "SIGILL (Illegal instruction — corrupted binary or bad jump)",
    "7": "SIGBUS (Bus error — misaligned memory access)",
    "9": "SIGKILL (Kill — OOM killer or explicit kill)",
}

CRASH_PATTERNS = {
    "segfault": r"(segmentation fault|segfault|sigsegv|signal 11)",
    "heap_corruption": r"(double free|heap corruption|invalid pointer|corrupted|malloc_printerr)",
    "stack_overflow": r"(stack overflow|stack smashing|__stack_chk_fail)",
    "null_deref": r"(null pointer|nullptr|dereference.*null|address 0x0)",
    "oom": r"(out of memory|oom|cannot allocate|malloc.*failed)",
    "use_after_free": r"(use.after.free|uaf|dangling pointer)",
    "buffer_overflow": r"(buffer overflow|bounds check|out.of.bounds)",
    "division_by_zero": r"(division by zero|divide.*zero|sigfpe)",
    "assertion": r"(assertion.*failed|assert.*false|abort.*called)",
    "python_exception": r"(Traceback.*most recent|Error:|Exception:)",
}

def parse_crash_log(log_text: str) -> dict:
    """Extrae informacion estructurada de un crash log."""
    info = {
        "raw_length": len(log_text),
        "crash_type": "unknown",
        "signal": None,
        "signal_description": None,
        "address": None,
        "pid": None,
        "function": None,
        "file": None,
        "line": None,
        "stacktrace": [],
        "patterns_matched": [],
    }

    text_lower = log_text.lower()

    # Detect crash type
    for crash_type, pattern in CRASH_PATTERNS.items():
        if re.search(pattern, text_lower):
            info["crash_type"] = crash_type
            info["patterns_matched"].append(crash_type)

    # Extract signal number
    sig_match = re.search(r"signal\s+(\d+)", log_text, re.I)
    if sig_match:
        sig_num = sig_match.group(1)
        info["signal"] = sig_num
        info["signal_description"] = SIGNAL_NAMES.get(sig_num, f"Signal {sig_num}")

    # Extract fault address
    addr_match = re.search(r"(?:at address|fault addr|address)\s+(0x[0-9a-fA-F]+)", log_text, re.I)
    if addr_match:
        info["address"] = addr_match.group(1)

    # Extract PID
    pid_match = re.search(r"(?:pid|process)\s*[:\s]\s*(\d+)", log_text, re.I)
    if pid_match:
        info["pid"] = pid_match.group(1)

    # Extract stacktrace lines
    stack_patterns = [
        r"#\d+\s+0x[0-9a-fA-F]+ in (\S+)",    # GDB format
        r"at (\S+\.py):(\d+)",                  # Python format
        r"File \"(.+?)\", line (\d+)",           # Python traceback
        r"(\S+\.(?:c|cpp|go|rs)):\d+",         # C/C++/Go/Rust
    ]
    for pattern in stack_patterns:
        matches = re.findall(pattern, log_text)
        if matches:
            info["stacktrace"].extend(str(m) for m in matches[:10])

    # Extract most relevant function/file/line
    func_match = re.search(r"in (\w+)\s+\(", log_text)
    if func_match:
        info["function"] = func_match.group(1)

    py_trace = re.search(r'File "(.+?)", line (\d+), in (\w+)', log_text)
    if py_trace:
        info["file"] = py_trace.group(1)
        info["line"] = int(py_trace.group(2))
        info["function"] = py_trace.group(3)

    return info

def _gdb_analyze(binary: str, core: str | None = None) -> str | None:
    import shutil
    if not shutil.which("gdb"):
        return None
    try:
        cmd = ["gdb", "--batch", binary]
        if core:
            cmd.extend([core])
        cmd.extend(["-ex", "bt", "-ex", "info registers", "-ex", "quit"])
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.stdout + r.stderr
    except Exception:
        return None

def cmd_analyze(args) -> int:
    log_path = Path(args.crash_log)
    if not log_path.exists():
        print(f"[evol-crash] File not found: {log_path}")
        return 1

    log_text = log_path.read_text(encoding="utf-8", errors="ignore")
    parsed = parse_crash_log(log_text)

    provider = _load_provider()

    # Generate hypothesis with LLM
    prompt = f"""Crash root-cause analysis:

Crash type: {parsed['crash_type']}
Signal: {parsed.get('signal_description', 'Unknown')}
Fault address: {parsed.get('address', 'Unknown')}
Function: {parsed.get('function', 'Unknown')}
File: {parsed.get('file', 'Unknown')}:{parsed.get('line', 'Unknown')}

Stack trace (top frames):
{chr(10).join(parsed['stacktrace'][:5]) or 'Not available'}

Raw log excerpt (first 500 chars):
{log_text[:500]}

Provide:
1. ROOT_CAUSE: Most likely cause (1-2 sentences)
2. REPRODUCTION: How to reproduce (steps)
3. FIX_HINT: Suggested fix direction
4. CONFIDENCE: High/Medium/Low

Format: JSON with keys: root_cause, reproduction_steps (list), fix_hint, confidence"""

    hypothesis = None
    try:
        response = provider.complete(
            system="You are a crash analysis expert. Be precise and actionable.",
            user=prompt
        ) if provider else "[Install evol-provider.py with EVOL_PROVIDER=anthropic for LLM analysis]"

        json_match = re.search(r'\{[^{}]+\}', response, re.S)
        if json_match:
            hypothesis = json.loads(json_match.group())
        else:
            hypothesis = {"root_cause": response, "confidence": "Low"}
    except Exception as e:
        hypothesis = {"root_cause": f"Analysis failed: {e}", "confidence": "Low"}

    result = {
        "timestamp": _now(),
        "crash_log": str(log_path),
        "parsed": parsed,
        "hypothesis": hypothesis,
    }

    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2))
        print(f"[evol-crash] Analysis → {args.output}")
    else:
        print(json.dumps(result, indent=2))
    return 0

def cmd_hypothesis(args) -> int:
    return cmd_analyze(args)

def cmd_reproduce(args) -> int:
    log_text = Path(args.crash_log).read_text(encoding="utf-8", errors="ignore")
    parsed = parse_crash_log(log_text)
    print(f"[evol-crash] Attempting reproduction with gdb...")
    gdb_out = _gdb_analyze(args.binary)
    if gdb_out:
        print(gdb_out)
    else:
        print("[evol-crash] gdb not available. Install gdb for crash reproduction.")
        print(f"[evol-crash] Crash type: {parsed['crash_type']}")
        print(f"[evol-crash] Signal: {parsed.get('signal_description', 'Unknown')}")
        print(f"[evol-crash] Patterns: {', '.join(parsed['patterns_matched'])}")
    return 0

def main(argv=None):
    p = argparse.ArgumentParser(prog="evol-crash", description=__doc__)
    p.add_argument("--output", "-o", default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("analyze")
    pa.add_argument("crash_log")

    ph = sub.add_parser("hypothesis")
    ph.add_argument("crash_log")

    pr = sub.add_parser("reproduce")
    pr.add_argument("crash_log")
    pr.add_argument("binary")

    args = p.parse_args(argv)
    return {"analyze": cmd_analyze, "hypothesis": cmd_hypothesis, "reproduce": cmd_reproduce}[args.cmd](args)

if __name__ == "__main__":
    sys.exit(main())
