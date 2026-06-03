#!/usr/bin/env python3
"""evol-patch — Generacion de patches para findings de seguridad.

Lee findings de evol-scan o evol-validate y genera fixes especificos.

Comandos:
  suggest <findings.json> [--id FINDING-NNN]   — genera sugerencias de patch
  apply <findings.json> --id FINDING-NNN        — aplica patch al archivo (con backup)
  diff <original> <patched>                     — muestra diff entre archivos
"""
from __future__ import annotations
import argparse, difflib, json, os, shutil, sys
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

def _llm(provider, prompt: str) -> str:
    if provider is None:
        return "# [Patch generation requires EVOL_PROVIDER=anthropic]\n# Remediation: " + prompt[:200]
    try:
        return provider.complete(
            system="You are a security engineer. Generate minimal, correct security patches. Return only the fixed code, no explanations outside comments.",
            user=prompt
        )
    except Exception as e:
        return f"# LLM error: {e}\n"

def generate_patch(finding: dict, provider) -> dict:
    file_path = Path(finding.get("file", ""))
    line_no = finding.get("line", 0)
    snippet = finding.get("code_snippet", "")
    remediation = finding.get("remediation", "")
    type_ = finding.get("type", "")

    # Read context around the vulnerable line
    context = ""
    if file_path.exists() and line_no > 0:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        start = max(0, line_no - 5)
        end = min(len(lines), line_no + 5)
        context = "\n".join(f"{i+1}: {l}" for i, l in enumerate(lines[start:end], start))

    prompt = f"""Security patch generation:

Vulnerability: {type_}
File: {file_path}
Line: {line_no}
Vulnerable code:
{snippet}

Context (lines around vulnerability):
{context}

Required fix: {remediation}

Generate a minimal, correct patch:
1. Show the BEFORE (vulnerable) code
2. Show the AFTER (fixed) code
3. Explain why the fix works in 1 sentence

Format:
BEFORE:
<vulnerable code>

AFTER:
<fixed code>

REASON: <one sentence explanation>"""

    response = _llm(provider, prompt)
    return {
        "finding_id": finding.get("id"),
        "severity": finding.get("severity"),
        "file": str(file_path),
        "line": line_no,
        "type": type_,
        "patch_suggestion": response,
        "remediation": remediation,
        "generated_at": _now(),
    }

def cmd_suggest(args) -> int:
    data = json.loads(Path(args.findings_json).read_text())
    findings = data.get("findings", data.get("results", []))
    # Handle evol-validate output
    if findings and "finding" in findings[0]:
        findings = [r["finding"] for r in findings if r.get("summary", {}).get("verdict") == "TRUE_POSITIVE"]

    if args.finding_id:
        findings = [f for f in findings if f.get("id") == args.finding_id]

    if not findings:
        print("[evol-patch] No findings to patch")
        return 0

    provider = _load_provider()
    patches = []
    for i, finding in enumerate(findings, 1):
        print(f"[evol-patch] Generating patch {i}/{len(findings)}: {finding.get('id')}", file=sys.stderr)
        patches.append(generate_patch(finding, provider))

    result = {"timestamp": _now(), "patches": patches}
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2))
        print(f"[evol-patch] {len(patches)} patches → {args.output}")
    else:
        print(json.dumps(result, indent=2))
    return 0

def cmd_apply(args) -> int:
    data = json.loads(Path(args.findings_json).read_text())
    findings = data.get("findings", [])
    finding = next((f for f in findings if f.get("id") == args.finding_id), None)
    if not finding:
        print(f"[evol-patch] Finding {args.finding_id} not found")
        return 1

    file_path = Path(finding["file"])
    if not file_path.exists():
        print(f"[evol-patch] File not found: {file_path}")
        return 1

    # Backup
    backup = file_path.with_suffix(file_path.suffix + ".bak")
    shutil.copy2(file_path, backup)
    print(f"[evol-patch] Backup → {backup}")
    print(f"[evol-patch] NOTE: Review the patch suggestion and apply manually.")
    print(f"[evol-patch] Patch for {finding['id']}:")
    print(f"  File: {file_path}:{finding.get('line')}")
    print(f"  Remediation: {finding.get('remediation')}")
    return 0

def cmd_diff(args) -> int:
    orig = Path(args.original).read_text(encoding="utf-8", errors="ignore").splitlines()
    patched = Path(args.patched).read_text(encoding="utf-8", errors="ignore").splitlines()
    diff = list(difflib.unified_diff(orig, patched, fromfile=args.original, tofile=args.patched, lineterm=""))
    print("\n".join(diff))
    return 0

def main(argv=None):
    p = argparse.ArgumentParser(prog="evol-patch", description=__doc__)
    p.add_argument("--output", "-o", default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("suggest")
    ps.add_argument("findings_json")
    ps.add_argument("--id", dest="finding_id", default=None)

    pa = sub.add_parser("apply")
    pa.add_argument("findings_json")
    pa.add_argument("--id", dest="finding_id", required=True)

    pd = sub.add_parser("diff")
    pd.add_argument("original")
    pd.add_argument("patched")

    args = p.parse_args(argv)
    return {"suggest": cmd_suggest, "apply": cmd_apply, "diff": cmd_diff}[args.cmd](args)

if __name__ == "__main__":
    sys.exit(main())
