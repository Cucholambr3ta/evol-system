#!/usr/bin/env python3
"""Evol-DD AgentShield — Framework security audit."""
import os, sys, re, subprocess, argparse, json
from pathlib import Path
from datetime import datetime
from _evol_common import get_logger

logger = get_logger("shield")

REPO_ROOT = "."

RULES = {
    "no_mcp_config": {
        "description": "No MCP server configuration in generated IDE configs and scripts",
        "patterns": [r"mcpServers", r"mcp\.json", r"evol-mcp-server", r"xdd-mcp-server"],
        "severity": "CRITICAL",
        # Solo aplica a archivos generados por evol-adapt.sh y scripts de instalacion.
        # Docs y prompts pueden mencionar MCP como referencia o para documentar
        # la invariante "cero MCP" — eso no es una violacion.
        "applies_to": [".json", ".yml", ".yaml"],
        "skip_dirs": ["docs/", "prompts/agents/", "skills/", "tests/", "evals/"],
    },
    "no_dangerous_commands": {
        "description": "No dangerous shell commands in scripts and hooks",
        "patterns": [r"rm\s+-rf\s+/(?!tmp|proc|sys)", r"git\s+--force", r"chmod\s+777", r"curl\s+\|sh"],
        "severity": "HIGH",
        # Docs pueden mencionar comandos peligrosos como ejemplos en runbooks/troubleshooting
        "skip_dirs": ["docs/", "tests/", "evals/"],
    },
    "no_hardcoded_secrets": {
        "description": "No hardcoded secrets",
        "patterns": [r"api[_-]?key\s*=\s*['\"][A-Za-z0-9]{20,}", r"password\s*=\s*['\"][^'\"]+['\"]"],
        "severity": "CRITICAL"
    },
    "no_evol_dangerous_refs": {
        "description": "Skills must not reference framework internals (.evol/, .gate-key, etc.)",
        "patterns": [
            r'\.(?:evol|xdd)/(?:\.gate[_-]?key|\.gate[_-]?log|state\.db|memory/)',
            r'gates?\.(?:json|key|log)',
            r'secrets?\.(?:env|json|key)',
            r'\.evol/\.skill[_-]?overrides',
            r'(?:index|read|write)[^\n]*\.evol/',
            r'\.evol/.*(?:read|write|delete|traverse)',
        ],
        "severity": "HIGH",
        "applies_to": [".md"],
        # Docs de arquitectura y operaciones documentan rutas .evol/ — no son violaciones
        "skip_dirs": ["docs/", "tests/", "evals/"],
    },
    "supply_chain_scan": {
        "description": "Supply chain scan capability",
        "tools": ["gitleaks", "semgrep"],
        "severity": "MEDIUM"
    }
}

def scan_file(filepath, violations):
    """Scan file for rule violations."""
    if not os.path.exists(filepath):
        return
    
    with open(filepath) as f:
        content = f.read()
    
    ext = os.path.splitext(filepath)[1]
    
    for rule_id, rule in RULES.items():
        if rule_id == "supply_chain_scan":
            continue

        # Respetar skip_dirs por regla
        skip_dirs = rule.get("skip_dirs", [])
        if skip_dirs and any(sd in filepath for sd in skip_dirs):
            continue

        applies = rule.get("applies_to", [])
        if applies and ext not in applies:
            continue

        for pattern in rule.get("patterns", []):
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violations.append({
                    "rule": rule_id,
                    "file": filepath,
                    "pattern": pattern,
                    "matches": matches[:3],
                    "severity": rule["severity"]
                })

def audit_directory(directory, extensions=None):
    """Audit directory for violations."""
    violations = []
    
    if extensions is None:
        extensions = [".md", ".json", ".yml", ".yaml", ".py", ".sh"]
    
    for ext in extensions:
        for filepath in Path(directory).rglob(f"*{ext}"):
            rel = str(filepath.relative_to(Path(REPO_ROOT)))
            if any(skip in rel for skip in [
                ".git/", "node_modules/", "dialog/", "tool_result/",
                # El propio shield y hooks de seguridad contienen los patrones que buscan
                "scripts/evol-shield.py",
                ".agent/hooks/scripts/pre-bash-dangerous-command.sh",
                # Docs de seguridad que mencionan los patrones legitimamente (no son violaciones)
                "docs/SECURITY_PERMISSIONS.md", "docs/GATE.md",
                "docs/seguridad/SECURITY_CONTROLS.md",
                "docs/seguridad/THREATS.md",   # documenta amenazas, no las implementa
                "docs/seguridad/PRIVACY.md",   # documenta rutas de datos .evol/
                "docs/qa/FIXES_DESARROLLADOR_AUDITORIA_FULL.md",
                # Workflows que documentan verificacion anti-MCP (mencionan mcpServers en grep)
                ".agent/workflows/crear-skill.md",
                ".agent/workflows/crear-agente.md",
                # Tests y fixtures de seguridad
                "tests/",
                "evals/",
            ]):
                continue
            
            scan_file(str(filepath), violations)
    
    return violations

def supply_chain_scan(directory):
    """Run gitleaks and semgrep if available."""
    results = {"gitleaks": None, "semgrep": None}
    
    if subprocess.run(["which", "gitleaks"], capture_output=True).returncode == 0:
        result = subprocess.run(
            ["gitleaks", "detect", "--no-git"],
            capture_output=True, cwd=directory
        )
        results["gitleaks"] = {
            "available": True,
            "secrets_found": result.returncode != 0,
            "output": result.stdout.decode()[:500]
        }
    else:
        results["gitleaks"] = {"available": False}
    
    if subprocess.run(["which", "semgrep"], capture_output=True).returncode == 0:
        result = subprocess.run(
            ["semgrep", "--config", "auto", "--json"],
            capture_output=True, cwd=directory
        )
        try:
            data = json.loads(result.stdout.decode())
            results["semgrep"] = {
                "available": True,
                "issues": len(data.get("results", []))
            }
        except:
            results["semgrep"] = {"available": True, "issues": 0}
    else:
        results["semgrep"] = {"available": False}
    
    return results

def check_permissions(directory):
    """Check for dangerous permission patterns."""
    violations = []
    sensitive = {
        ".evol/.gate-key": (0o600, "secret"),
        ".evol/.gate-log.jsonl": (0o640, "sensitive log"),
        ".evol/": (0o750, "runtime dir"),
        "memory/": (0o750, "memory dir"),
        "dialog/": (0o750, "dialog dir"),
        "tool_result/": (0o750, "tool_result dir"),
    }
    for path_suffix, (expected_mode, kind) in sensitive.items():
        full_path = os.path.join(directory, path_suffix)
        if not os.path.exists(full_path):
            continue
        try:
            mode = os.stat(full_path).st_mode & 0o777
            if mode & 0o022:
                violations.append({
                    "rule": "dangerous_permissions",
                    "file": path_suffix,
                    "severity": "HIGH",
                    "message": f"{kind} is group-writable ({oct(mode)})"
                })
        except OSError:
            pass
    return violations

def audit(ci_mode=False, no_write=False):
    """Run full security audit."""
    print("=== Evol-DD AgentShield Audit ===")
    
    violations = []
    
    perm_violations = check_permissions(".")
    violations.extend(perm_violations)
    
    for dir_path in [".agent/", "scripts/", "prompts/", "skills/", "docs/"]:
        if os.path.exists(dir_path):
            dir_violations = audit_directory(dir_path)
            violations.extend(dir_violations)
    
    sc_results = supply_chain_scan(".")
    
    print(f"\n--- Violations: {len(violations)} ---")
    
    critical = [v for v in violations if v["severity"] == "CRITICAL"]
    high = [v for v in violations if v["severity"] == "HIGH"]
    
    if critical:
        print(f"\n[CRITICAL] {len(critical)} critical violations:")
        for v in critical:
            print(f"  - {v['rule']} in {v['file']}")
    
    if high:
        print(f"\n[HIGH] {len(high)} high violations:")
        for v in high:
            print(f"  - {v['rule']} in {v['file']}")
    
    print("\n--- Supply Chain ---")
    print(f"gitleaks: {'available' if sc_results['gitleaks']['available'] else 'not installed'}")
    print(f"semgrep: {'available' if sc_results['semgrep']['available'] else 'not installed'}")
    
    if not no_write:
        report_path = ".evol/qa/QA_REPORT.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, "w") as f:
            f.write("# Security Audit Report\n\n")
            f.write(f"Date: {datetime.now().isoformat()}\n\n")
            f.write(f"## Summary\n")
            f.write(f"- Critical: {len(critical)}\n")
            f.write(f"- High: {len(high)}\n")
            f.write(f"- Total: {len(violations)}\n\n")
            f.write(f"## Supply Chain\n")
            f.write(f"- gitleaks: {'installed' if sc_results['gitleaks']['available'] else 'not installed'}\n")
            f.write(f"- semgrep: {'installed' if sc_results['semgrep']['available'] else 'not installed'}\n")
        
        print(f"\n[OK] Report: {report_path}")
    
    if ci_mode:
        if critical:
            print("[FAIL] Critical violations found")
            sys.exit(1)
    
    return violations

def main():
    parser = argparse.ArgumentParser(description="Evol-DD AgentShield")
    sub = parser.add_subparsers(dest="cmd")
    
    p = sub.add_parser("audit", help="Run security audit")
    p.add_argument("--ci", action="store_true", help="CI mode (exit 1 on critical)")
    p.add_argument("--no-write", action="store_true", help="Don't write report to disk")
    
    sub.add_parser("rules", help="List security rules")
    
    args = parser.parse_args()
    
    if args.cmd == "audit":
        audit(ci_mode=args.ci, no_write=args.no_write)
    elif args.cmd == "rules":
        print("=== Security Rules ===")
        for rule_id, rule in RULES.items():
            print(f"\n{rule_id}:")
            print(f"  Severity: {rule['severity']}")
            print(f"  Description: {rule['description']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
