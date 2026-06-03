#!/usr/bin/env python3
"""evol-validate — Pipeline multi-stage de validacion de findings de seguridad.

Valida si un finding de evol-scan es realmente exploitable.
5 stages: 0 (inventario) → A (assessment) → B (analysis) → C (ruling) → D (report)

Uso:
  evol-validate <findings.json>                    — valida todos los findings
  evol-validate <findings.json> --id FINDING-NNN   — valida finding especifico
  evol-validate <findings.json> --severity HIGH     — valida por severidad minima
  evol-validate <findings.json> --output report.json
"""
from __future__ import annotations
import argparse, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]

def _now(): return datetime.now(timezone.utc).isoformat()

def _load_provider():
    """Carga evol-provider.py si disponible. Retorna provider o None."""
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

def _llm_complete(provider, prompt: str) -> str:
    if provider is None:
        return "[LLM not available — install evol-provider.py and set EVOL_PROVIDER=anthropic]"
    try:
        return provider.complete(system="You are a security validation expert. Be concise and structured.", user=prompt)
    except Exception as e:
        return f"[LLM error: {e}]"

# ── Stage implementations ─────────────────────────────────────────────────────

def stage_0_inventory(finding: dict) -> dict:
    """Stage 0: Inventario basico del finding."""
    file_path = Path(finding.get("file", ""))
    exists = file_path.exists()
    size = file_path.stat().st_size if exists else 0
    lang = file_path.suffix.lower()
    return {
        "stage": "0-inventory",
        "file_exists": exists,
        "file_size": size,
        "lang": lang,
        "line": finding.get("line", 0),
        "severity": finding.get("severity"),
        "type": finding.get("type"),
    }

def stage_a_assessment(finding: dict, provider) -> dict:
    """Stage A: LLM assessment de reachability."""
    prompt = f"""Security finding assessment:

Finding ID: {finding.get('id')}
Severity: {finding.get('severity')}
Type: {finding.get('type')}
File: {finding.get('file')}
Line: {finding.get('line')}
Code snippet: {finding.get('code_snippet', 'N/A')}
Description: {finding.get('description')}

Answer these questions concisely:
1. REACHABILITY: Is this code path reachable from untrusted input? (Yes/No/Unknown)
2. EXPLOITABILITY: Can this be exploited reliably? (Yes/No/Unlikely)
3. IMPACT: What can an attacker achieve? (1 sentence)
4. CONFIDENCE: How confident are you? (High/Medium/Low)

Format: JSON with keys: reachability, exploitability, impact, confidence, notes"""
    response = _llm_complete(provider, prompt)
    try:
        # Try to extract JSON from response
        import re
        json_match = re.search(r'\{[^{}]+\}', response, re.S)
        if json_match:
            return {"stage": "A-assessment", **json.loads(json_match.group())}
    except Exception:
        pass
    return {"stage": "A-assessment", "raw_response": response, "reachability": "Unknown", "confidence": "Low"}

def stage_b_analysis(finding: dict, stage_a: dict, provider) -> dict:
    """Stage B: Source-to-sink tracing mental."""
    reachability = stage_a.get("reachability", "Unknown")
    prompt = f"""Deep security analysis:

Finding: {finding.get('description')}
Code: {finding.get('code_snippet', 'N/A')}
Previous assessment: reachability={reachability}

Perform source-to-sink analysis:
1. SOURCE: Where does user-controlled data enter?
2. SINK: Where does it reach the vulnerable function?
3. SANITIZATION: Are there any sanitization/validation steps in the path?
4. BYPASS: Can the sanitization be bypassed?

Conclude: Is this a TRUE_POSITIVE or FALSE_POSITIVE?
Format: JSON with keys: source, sink, sanitization_present, bypass_possible, verdict (TRUE_POSITIVE/FALSE_POSITIVE/UNCERTAIN), explanation"""
    response = _llm_complete(provider, prompt)
    try:
        import re
        json_match = re.search(r'\{[^{}]+\}', response, re.S)
        if json_match:
            return {"stage": "B-analysis", **json.loads(json_match.group())}
    except Exception:
        pass
    return {"stage": "B-analysis", "raw_response": response, "verdict": "UNCERTAIN"}

def stage_c_ruling(finding: dict, stage_b: dict, provider) -> dict:
    """Stage C: CVSS ruling y disqualifiers."""
    verdict = stage_b.get("verdict", "UNCERTAIN")
    prompt = f"""Security ruling for confirmed finding:

Finding type: {finding.get('type')}
Severity: {finding.get('severity')}
Analysis verdict: {verdict}
Bypass possible: {stage_b.get('bypass_possible', 'Unknown')}

Provide CVSS 3.1 base score estimate:
- Attack Vector (Network/Adjacent/Local/Physical)
- Attack Complexity (Low/High)
- Privileges Required (None/Low/High)
- User Interaction (None/Required)
- Scope (Unchanged/Changed)
- Confidentiality/Integrity/Availability Impact (None/Low/High)

Also: list any DISQUALIFIERS that would reduce severity (auth required, limited scope, etc.)

Format: JSON with keys: cvss_vector, base_score, disqualifiers (list), final_severity"""
    response = _llm_complete(provider, prompt)
    try:
        import re
        json_match = re.search(r'\{[^{}]+\}', response, re.S)
        if json_match:
            return {"stage": "C-ruling", **json.loads(json_match.group())}
    except Exception:
        pass
    return {"stage": "C-ruling", "raw_response": response, "final_severity": finding.get("severity")}

def stage_d_report(finding: dict, stages: dict) -> dict:
    """Stage D: Reporte final consolidado."""
    verdict = stages.get("B", {}).get("verdict", "UNCERTAIN")
    final_severity = stages.get("C", {}).get("final_severity", finding.get("severity"))
    return {
        "stage": "D-report",
        "finding_id": finding.get("id"),
        "verdict": verdict,
        "original_severity": finding.get("severity"),
        "validated_severity": final_severity,
        "reachability": stages.get("A", {}).get("reachability", "Unknown"),
        "exploitability": stages.get("A", {}).get("exploitability", "Unknown"),
        "impact": stages.get("A", {}).get("impact", "Unknown"),
        "cvss_score": stages.get("C", {}).get("base_score", "N/A"),
        "cvss_vector": stages.get("C", {}).get("cvss_vector", "N/A"),
        "disqualifiers": stages.get("C", {}).get("disqualifiers", []),
        "remediation": finding.get("remediation", ""),
        "validated_at": _now(),
    }


def validate_finding(finding: dict, provider) -> dict:
    stages = {}
    stages["0"] = stage_0_inventory(finding)
    stages["A"] = stage_a_assessment(finding, provider)
    stages["B"] = stage_b_analysis(finding, stages["A"], provider)
    stages["C"] = stage_c_ruling(finding, stages["B"], provider)
    stages["D"] = stage_d_report(finding, stages)
    return {"finding": finding, "validation": stages, "summary": stages["D"]}


def main(argv=None):
    p = argparse.ArgumentParser(prog="evol-validate", description=__doc__)
    p.add_argument("findings_json", help="Output de evol-scan (JSON)")
    p.add_argument("--id", dest="finding_id", default=None)
    p.add_argument("--severity", default="HIGH", choices=SEVERITY_ORDER)
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args(argv)

    data = json.loads(Path(args.findings_json).read_text())
    findings = data.get("findings", [])

    # Filter
    min_idx = SEVERITY_ORDER.index(args.severity)
    to_validate = [
        f for f in findings
        if (args.finding_id is None or f["id"] == args.finding_id)
        and SEVERITY_ORDER.index(f.get("severity", "INFO")) <= min_idx
    ]

    if not to_validate:
        print(f"[evol-validate] No findings match criteria (severity>={args.severity})")
        return 0

    provider = _load_provider()
    if provider is None:
        print("[evol-validate] WARN: No LLM provider — stages A-C will return stubs", file=sys.stderr)

    results = []
    for i, finding in enumerate(to_validate, 1):
        print(f"[evol-validate] Validating {i}/{len(to_validate)}: {finding['id']} ({finding['severity']})", file=sys.stderr)
        result = validate_finding(finding, provider)
        results.append(result)

    report = {
        "timestamp": _now(),
        "total_validated": len(results),
        "true_positives": sum(1 for r in results if r["summary"]["verdict"] == "TRUE_POSITIVE"),
        "false_positives": sum(1 for r in results if r["summary"]["verdict"] == "FALSE_POSITIVE"),
        "uncertain": sum(1 for r in results if r["summary"]["verdict"] == "UNCERTAIN"),
        "results": results,
    }

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2))
        print(f"[evol-validate] Report → {args.output}")
    else:
        print(json.dumps(report, indent=2))

    # Exit code: 2 if any TRUE_POSITIVE CRITICAL, 1 if any TRUE_POSITIVE HIGH
    true_pos = [r for r in results if r["summary"]["verdict"] == "TRUE_POSITIVE"]
    if any(r["summary"]["validated_severity"] == "CRITICAL" for r in true_pos):
        return 2
    if any(r["summary"]["validated_severity"] == "HIGH" for r in true_pos):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
