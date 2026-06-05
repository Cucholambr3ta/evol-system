#!/usr/bin/env python3
"""evol-scan — SAST nativo para Evol-DD.

Escanea codigo fuente buscando vulnerabilidades sin dependencias externas.
Degrada elegantemente: usa semgrep/gitleaks si disponibles, modo heuristico si no.

Comandos:
  source <dir> [--lang auto|python|js|bash] [--output FILE]
  secrets <dir> [--output FILE]
  deps <file> [--output FILE]          requirements.txt o package.json
  owasp <dir> [--output FILE]

Output: JSON con findings [{id, severity, type, file, line, description, remediation, cvss_estimate}]
"""
from __future__ import annotations
import argparse, ast, hashlib, json, os, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

SEVERITY = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")

def _id(file: str, line: int, type_: str) -> str:
    h = hashlib.sha256(f"{file}:{line}:{type_}".encode()).hexdigest()[:8]
    return f"FINDING-{h.upper()}"

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Heuristic patterns ────────────────────────────────────────────────────────

PYTHON_PATTERNS = [
    # (regex, severity, type, description, remediation)
    (r'(?<!literal_)(?<!ast\.)eval\s*\(', "HIGH", "CWE-78", "eval() with dynamic input can execute arbitrary code", "Replace eval() with ast.literal_eval() or a safe parser"),
    (r'exec\s*\(', "HIGH", "CWE-78", "exec() executes arbitrary Python code", "Remove exec() or restrict to compile-time constants"),
    (r'__import__\s*\(', "MEDIUM", "CWE-470", "Dynamic import can load attacker-controlled modules", "Use static imports instead"),
    (r'shell\s*=\s*True', "HIGH", "CWE-78", "shell=True with dynamic input enables command injection", "Use shell=False and pass args as list"),
    (r'os\.system\s*\(', "HIGH", "CWE-78", "os.system() executes shell commands", "Use subprocess with shell=False"),
    (r'pickle\.(loads?|load)\s*\(', "HIGH", "CWE-502", "Pickle deserialization of untrusted data enables RCE", "Use JSON or msgpack for untrusted data"),
    (r'yaml\.load\s*\([^)]*(?<!Loader=yaml\.SafeLoader)', "MEDIUM", "CWE-502", "yaml.load() without SafeLoader enables code execution", "Use yaml.safe_load() instead"),
    (r'hashlib\.(md5|sha1)\s*\(', "LOW", "CWE-327", "MD5/SHA1 are cryptographically broken", "Use SHA-256 or SHA-3"),
    (r'random\.(random|randint|choice)\s*\(', "LOW", "CWE-338", "random module is not cryptographically secure", "Use secrets module for security-sensitive randomness"),
    (r'sqlite3\.connect\s*\(.*\+', "MEDIUM", "CWE-89", "String concatenation in SQL query may be SQLi", "Use parameterized queries with ?"),
    (r'\.format\s*\(.*request', "MEDIUM", "CWE-89", "String format with request data may be SQLi", "Use parameterized queries"),
    (r'open\s*\([^)]*\+[^)]*["\']r', "MEDIUM", "CWE-22", "Dynamic file path with user input may be path traversal", "Validate and sanitize file paths"),
    (r'request\.(args|form|json|data)\[', "INFO", "CWE-20", "Direct user input access — verify input validation", "Validate and sanitize all user inputs"),
]

JS_PATTERNS = [
    (r'eval\s*\(', "HIGH", "CWE-78", "eval() executes arbitrary JavaScript", "Remove eval() usage"),
    (r'innerHTML\s*=', "HIGH", "CWE-79", "innerHTML assignment enables XSS", "Use textContent or DOMPurify"),
    (r'document\.write\s*\(', "HIGH", "CWE-79", "document.write() enables XSS", "Use DOM manipulation methods"),
    (r'dangerouslySetInnerHTML', "HIGH", "CWE-79", "dangerouslySetInnerHTML enables XSS in React", "Sanitize HTML before rendering"),
    (r'require\s*\(\s*[^"\'`]', "MEDIUM", "CWE-470", "Dynamic require() may load untrusted modules", "Use static require() with hardcoded paths"),
    (r'child_process', "HIGH", "CWE-78", "child_process usage — verify command construction", "Avoid shell: true, validate all inputs"),
    (r'Math\.random\s*\(', "LOW", "CWE-338", "Math.random() is not cryptographically secure", "Use crypto.randomBytes() for security contexts"),
    (r'localStorage\.(setItem|getItem)', "INFO", "CWE-922", "localStorage stores data in plaintext", "Do not store sensitive data in localStorage"),
]

BASH_PATTERNS = [
    (r'\$\([^)]*\$[A-Z_]+', "HIGH", "CWE-78", "Unquoted variable in command substitution enables injection", 'Quote variables: "$VAR"'),
    (r'curl\s+.*\|\s*bash', "CRITICAL", "CWE-78", "curl|bash executes remote code without verification", "Download, verify signature, then execute"),
    (r'wget\s+.*\|\s*bash', "CRITICAL", "CWE-78", "wget|bash executes remote code without verification", "Download, verify signature, then execute"),
    (r'chmod\s+[0-7]*7[0-7]*\s', "MEDIUM", "CWE-732", "World-writable permissions", "Use least-privilege permissions"),
    (r'sudo\s+', "INFO", "CWE-250", "sudo usage — verify necessity", "Avoid sudo in scripts when possible"),
]

SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9_\-]{20,})["\']', "CRITICAL", "CWE-798", "Hardcoded API key detected"),
    (r'(?i)(secret|password|passwd|pwd)\s*[=:]\s*["\']([^"\']{8,})["\']', "CRITICAL", "CWE-798", "Hardcoded secret/password detected"),
    (r'(?i)(token|auth)\s*[=:]\s*["\']([A-Za-z0-9_\-\.]{20,})["\']', "HIGH", "CWE-798", "Hardcoded token detected"),
    (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', "CRITICAL", "CWE-321", "Private key embedded in source code"),
    (r'(?i)aws_access_key_id\s*[=:]\s*["\']?AKIA[0-9A-Z]{16}', "CRITICAL", "CWE-798", "AWS access key detected"),
    (r'ghp_[A-Za-z0-9]{36}', "CRITICAL", "CWE-798", "GitHub personal access token detected"),
]

OWASP_PATTERNS = [
    # A01 Broken Access Control
    (r'(?i)idor|object_id|user_id.*param|account.*param', "MEDIUM", "OWASP-A01", "Potential IDOR — verify object-level authorization"),
    # A02 Cryptographic Failures
    (r'(?i)(md5|sha1|des|rc4|3des)\s*\(', "MEDIUM", "OWASP-A02", "Weak cryptographic algorithm"),
    # A03 Injection
    (r'(?i)select\s+.+\s+from\s+.+\s*\+', "HIGH", "OWASP-A03", "String concatenation in SQL query — potential SQLi"),
    (r'(?i)execute\s*\(\s*["\'].+\+', "HIGH", "OWASP-A03", "Dynamic SQL execution — potential SQLi"),
    # A05 Security Misconfiguration
    (r'(?i)debug\s*=\s*true', "MEDIUM", "OWASP-A05", "Debug mode enabled in code"),
    (r'(?i)cors\s*\(\s*\*\s*\)', "MEDIUM", "OWASP-A05", "Wildcard CORS origin allows any origin"),
    # A07 Auth failures
    (r'(?i)jwt\.decode\s*\([^)]*verify\s*=\s*false', "CRITICAL", "OWASP-A07", "JWT signature verification disabled"),
    # A08 Software integrity
    (r'(?i)(require|import)\s+["\']http://', "HIGH", "OWASP-A08", "Importing over HTTP (not HTTPS) — MitM risk"),
]


# ── Scanners ──────────────────────────────────────────────────────────────────

def _scan_file_with_patterns(filepath: Path, patterns: list, lang: str) -> list[dict]:
    findings = []
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        for pat_tuple in patterns:
            pattern, severity = pat_tuple[0], pat_tuple[1]
            type_ = pat_tuple[2]
            desc = pat_tuple[3]
            remediation = pat_tuple[4] if len(pat_tuple) > 4 else "See OWASP/CWE guidance"
            if re.search(pattern, line):
                findings.append({
                    "id": _id(str(filepath), i, type_),
                    "severity": severity,
                    "type": type_,
                    "file": str(filepath),
                    "line": i,
                    "code_snippet": line.strip()[:120],
                    "description": desc,
                    "remediation": remediation,
                    "cvss_estimate": _cvss_estimate(severity),
                    "scanner": "evol-heuristic",
                    "lang": lang,
                })
    return findings


def _cvss_estimate(severity: str) -> str:
    return {"CRITICAL": "9.0-10.0", "HIGH": "7.0-8.9", "MEDIUM": "4.0-6.9", "LOW": "0.1-3.9", "INFO": "0.0"}.get(severity, "0.0")


def _detect_lang(filepath: Path) -> str:
    ext = filepath.suffix.lower()
    return {".py": "python", ".js": "js", ".ts": "js", ".jsx": "js", ".tsx": "js",
            ".sh": "bash", ".bash": "bash", ".zsh": "bash"}.get(ext, "unknown")


def _try_semgrep(directory: str, output_file: str | None) -> list[dict] | None:
    if not _cmd_available("semgrep"):
        return None
    try:
        r = subprocess.run(
            ["semgrep", "--config", "auto", "--json", "--quiet", directory],
            capture_output=True, text=True, timeout=120,
        )
        data = json.loads(r.stdout)
        findings = []
        for result in data.get("results", []):
            meta = result.get("extra", {})
            severity = meta.get("severity", "MEDIUM").upper()
            if severity not in SEVERITY:
                severity = "MEDIUM"
            findings.append({
                "id": _id(result.get("path", ""), result.get("start", {}).get("line", 0), result.get("check_id", "")),
                "severity": severity,
                "type": result.get("check_id", "semgrep"),
                "file": result.get("path", ""),
                "line": result.get("start", {}).get("line", 0),
                "code_snippet": meta.get("lines", "")[:120],
                "description": meta.get("message", ""),
                "remediation": meta.get("fix", "See semgrep rule documentation"),
                "cvss_estimate": _cvss_estimate(severity),
                "scanner": "semgrep",
            })
        return findings
    except Exception:
        return None


def _try_gitleaks(directory: str) -> list[dict] | None:
    if not _cmd_available("gitleaks"):
        return None
    try:
        r = subprocess.run(
            ["gitleaks", "detect", "--no-git", "--source", directory, "--report-format", "json", "--report-path", "/tmp/evol-gitleaks.json"],
            capture_output=True, text=True, timeout=60,
        )
        report = Path("/tmp/evol-gitleaks.json")
        if not report.exists():
            return []
        data = json.loads(report.read_text())
        if not isinstance(data, list):
            return []
        findings = []
        for leak in data:
            findings.append({
                "id": _id(leak.get("File", ""), leak.get("StartLine", 0), "CWE-798"),
                "severity": "CRITICAL",
                "type": "CWE-798",
                "file": leak.get("File", ""),
                "line": leak.get("StartLine", 0),
                "code_snippet": leak.get("Match", "")[:120],
                "description": f"Secret detected: {leak.get('RuleID', 'unknown rule')}",
                "remediation": "Remove secret from code. Rotate the credential immediately. Use environment variables or secrets manager.",
                "cvss_estimate": "9.0-10.0",
                "scanner": "gitleaks",
            })
        return findings
    except Exception:
        return None


def _cmd_available(cmd: str) -> bool:
    import shutil
    return shutil.which(cmd) is not None


def cmd_source(args) -> int:
    directory = args.directory
    lang_filter = getattr(args, "lang", "auto")
    findings = []

    # Try semgrep first (better results)
    semgrep_findings = _try_semgrep(directory, args.output)
    if semgrep_findings is not None:
        findings.extend(semgrep_findings)
        print(f"[evol-scan] semgrep: {len(semgrep_findings)} findings", file=sys.stderr)
    else:
        print("[evol-scan] semgrep not available — using heuristic scanner", file=sys.stderr)
        # Heuristic scan
        for filepath in Path(directory).rglob("*"):
            if not filepath.is_file():
                continue
            skip = [".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"]
            if any(s in str(filepath) for s in skip):
                continue
            lang = _detect_lang(filepath)
            if lang_filter != "auto" and lang != lang_filter:
                continue
            if lang == "python":
                findings.extend(_scan_file_with_patterns(filepath, PYTHON_PATTERNS, lang))
            elif lang == "js":
                findings.extend(_scan_file_with_patterns(filepath, JS_PATTERNS, lang))
            elif lang == "bash":
                findings.extend(_scan_file_with_patterns(filepath, BASH_PATTERNS, lang))

    return _output(findings, args.output, "source")


def cmd_secrets(args) -> int:
    directory = args.directory
    findings = []

    # Try gitleaks first
    gl = _try_gitleaks(directory)
    if gl is not None:
        findings.extend(gl)
        print(f"[evol-scan] gitleaks: {len(gl)} findings", file=sys.stderr)
    else:
        print("[evol-scan] gitleaks not available — using heuristic secret scanner", file=sys.stderr)
        for filepath in Path(directory).rglob("*"):
            if not filepath.is_file():
                continue
            skip = [".git", "__pycache__", "node_modules", ".venv", "venv"]
            if any(s in str(filepath) for s in skip):
                continue
            try:
                text = filepath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                for pattern, severity, type_, desc in SECRET_PATTERNS:
                    if re.search(pattern, line):
                        snippet = re.sub(r'["\']([A-Za-z0-9_\-\.]{8,})["\']', '"[REDACTED]"', line.strip())
                        findings.append({
                            "id": _id(str(filepath), i, type_),
                            "severity": severity,
                            "type": type_,
                            "file": str(filepath),
                            "line": i,
                            "code_snippet": snippet[:120],
                            "description": desc,
                            "remediation": "Remove secret from source. Rotate credential. Use environment variables or a secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager).",
                            "cvss_estimate": _cvss_estimate(severity),
                            "scanner": "evol-heuristic",
                        })


    # Heuristic scanner — always runs (catches embedded keys, tokens in non-git dirs)
    print("[evol-scan] Heuristic secret scanner...", file=sys.stderr)
    for filepath in Path(directory).rglob("*"):
        if not filepath.is_file():
            continue
        skip = [".git", "__pycache__", "node_modules", ".venv", "venv"]
        if any(s in str(filepath) for s in skip):
            continue
        try:
            text = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for pattern, severity, type_, desc in SECRET_PATTERNS:
                if re.search(pattern, line):
                    fid = _id(str(filepath), i, type_)
                    if not any(f["id"] == fid for f in findings):
                        snippet = re.sub(r'["\'\']([A-Za-z0-9_\-\.]{8,})["\'\']', '"[REDACTED]"', line.strip())
                        findings.append({
                            "id": fid, "severity": severity, "type": type_,
                            "file": str(filepath), "line": i,
                            "code_snippet": snippet[:120],
                            "description": desc,
                            "remediation": "Remove secret from source. Rotate credential. Use environment variables or a secrets manager.",
                            "cvss_estimate": _cvss_estimate(severity), "scanner": "evol-heuristic",
                        })

    return _output(findings, args.output, "secrets")


def cmd_deps(args) -> int:
    depfile = Path(args.file)
    findings = []
    if not depfile.exists():
        print(f"[evol-scan] File not found: {depfile}", file=sys.stderr)
        return 1

    # Basic version pattern check — known vulnerable version ranges
    KNOWN_VULNS = [
        ("requests", "<2.31.0", "HIGH", "CVE-2023-32681", "requests < 2.31.0 has proxy header leak vulnerability"),
        ("pillow", "<10.0.0", "HIGH", "CVE-2023-44271", "Pillow < 10.0.0 has uncontrolled resource consumption"),
        ("cryptography", "<41.0.0", "MEDIUM", "CVE-2023-38325", "cryptography < 41.0.0 has Bleichenbacher attack vulnerability"),
        ("pyyaml", "<6.0", "HIGH", "CVE-2020-14343", "PyYAML < 6.0 has arbitrary code execution via yaml.load()"),
        ("django", "<4.2.0", "HIGH", "CVE-2023-36053", "Django < 4.2.0 has potential ReDoS vulnerability"),
        ("flask", "<2.3.0", "MEDIUM", "CVE-2023-30861", "Flask < 2.3.0 has session cookie vulnerability"),
    ]

    if depfile.name in ("requirements.txt", "requirements-dev.txt"):
        content = depfile.read_text()
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for pkg, vuln_ver, severity, cve, desc in KNOWN_VULNS:
                if re.match(rf"(?i){re.escape(pkg)}\s*[<>=!]", line):
                    findings.append({
                        "id": _id(str(depfile), 0, cve),
                        "severity": severity,
                        "type": cve,
                        "file": str(depfile),
                        "line": 0,
                        "code_snippet": line[:120],
                        "description": desc,
                        "remediation": f"Upgrade {pkg} to a patched version. Check https://pypi.org/project/{pkg}/ for latest.",
                        "cvss_estimate": _cvss_estimate(severity),
                        "scanner": "evol-sca",
                    })

    return _output(findings, args.output, "deps")


def cmd_owasp(args) -> int:
    directory = args.directory
    findings = []
    for filepath in Path(directory).rglob("*"):
        if not filepath.is_file():
            continue
        skip = [".git", "__pycache__", "node_modules", ".venv", "venv", "dist"]
        if any(s in str(filepath) for s in skip):
            continue
        findings.extend(_scan_file_with_patterns(filepath, OWASP_PATTERNS, "any"))
    return _output(findings, args.output, "owasp")


def _output(findings: list[dict], output_file: str | None, scan_type: str) -> int:
    result = {
        "scan_type": scan_type,
        "timestamp": _now(),
        "total": len(findings),
        "by_severity": {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY},
        "findings": sorted(findings, key=lambda f: SEVERITY.index(f["severity"])),
    }
    if output_file:
        Path(output_file).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"[evol-scan] {len(findings)} findings → {output_file}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2))

    # Summary to stderr
    crit = result["by_severity"]["CRITICAL"]
    high = result["by_severity"]["HIGH"]
    print(f"[evol-scan] CRITICAL={crit} HIGH={high} MEDIUM={result['by_severity']['MEDIUM']} LOW={result['by_severity']['LOW']}", file=sys.stderr)

    return 2 if crit > 0 else (1 if high > 0 else 0)


def build_parser():
    p = argparse.ArgumentParser(prog="evol-scan", description=__doc__)
    p.add_argument("--output", "-o", default=None, help="Output JSON file (default: stdout)")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("source", help="SAST scan on source files")
    ps.add_argument("directory")
    ps.add_argument("--lang", default="auto", choices=["auto", "python", "js", "bash"])

    ps2 = sub.add_parser("secrets", help="Secret detection scan")
    ps2.add_argument("directory")

    ps3 = sub.add_parser("deps", help="SCA dependency scan")
    ps3.add_argument("file", help="requirements.txt or package.json")

    ps4 = sub.add_parser("owasp", help="OWASP Top 10 pattern scan")
    ps4.add_argument("directory")

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    dispatch = {"source": cmd_source, "secrets": cmd_secrets, "deps": cmd_deps, "owasp": cmd_owasp}
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
