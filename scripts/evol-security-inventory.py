#!/usr/bin/env python3
"""evol-security-inventory — Arsenal de seguridad/pentest segun componentes de la historia.

El relato: "los test incluian TODAS las herramientas de seguridad, hackeo, etc que tenia
instalado el sistema". Evol-DD heredo de RAPTOR un arsenal nativo. Este script genera el bloque
de tareas STDD del checklist de cada historia, segun lo que la historia toca (relevancia por
componente), no genericamente.

Dos niveles:
  NIVEL 1 NATIVAS (Python stdlib, corren SIEMPRE, sin instalar): scan, shield, crash, patch,
    validate, STRIDE, fuzz estatico.
  NIVEL 2 EXTERNAS (auto-discovery via evol-doctor.sh --json, status==ok): semgrep, gitleaks,
    trivy, nuclei, OWASP ZAP. Evol-DD NO usa Shannon (AGPL) — exploit-verify es manual.

Comandos:
  checklist --components=auth,api,...  Genera bloque de tareas STDD para esos componentes
  readme                                Genera/actualiza seccion "Herramientas de Seguridad" en README
  list                                  Lista todo el arsenal (nativas + externas detectadas)

Reusa evol-doctor.sh --json para detectar externas instaladas.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


# ── Arsenal NIVEL 1 — nativas (siempre disponibles, sin instalar) ──────────────

NATIVE_TOOLS = {
    "evol-scan": {
        "tipo": "SAST", "comando": "python3 scripts/evol-scan.py source src/",
        "criterio": "0 findings HIGH/CRITICAL",
        "detecta": "SQLi (CWE-89), command injection (CWE-78), XSS, secrets",
    },
    "evol-shield": {
        "tipo": "Audit estatico", "comando": "python3 scripts/evol-shield.py audit --ci",
        "criterio": "0 CRITICAL",
        "detecta": "AgentShield 11 reglas",
    },
    "evol-crash": {
        "tipo": "Crash analysis", "comando": "python3 scripts/evol-crash.py analyze <log>",
        "criterio": "root-cause identificado",
        "detecta": "crash logs + core dumps + reproduce (gdb)",
    },
    "evol-patch": {
        "tipo": "Auto-fix", "comando": "python3 scripts/evol-patch.py <finding>",
        "criterio": "parche aplicado + test verde",
        "detecta": "genera parche para vuln detectada",
    },
    "evol-validate": {
        "tipo": "Validacion findings", "comando": "python3 scripts/evol-validate.py <finding>",
        "criterio": "finding confirmado (no falso positivo)",
        "detecta": "fact-check de findings (SIFT)",
    },
    "stride": {
        "tipo": "Threat modeling", "comando": "/sec STRIDE (threat modeling nativo)",
        "criterio": "amenazas STRIDE catalogadas con control",
        "detecta": "modelado de amenazas por componente",
    },
    "pruebas-fuzz": {
        "tipo": "Fuzzing estatico", "comando": "/pruebas-fuzz (sandbox aislado)",
        "criterio": "0 crashes con input malformado",
        "detecta": "inyeccion de datos malformados",
    },
}

# ── Arsenal NIVEL 2 — externas (auto-discovery) ────────────────────────────────

EXTERNAL_TOOLS = {
    "semgrep": {
        "tipo": "SAST avanzado", "comando": "semgrep --config=auto src/",
        "criterio": "0 findings ERROR", "install": "pip install semgrep",
    },
    "gitleaks": {
        "tipo": "Secrets scan", "comando": "gitleaks detect --source=.",
        "criterio": "0 secretos", "install": "https://github.com/gitleaks/gitleaks",
    },
    "trivy": {
        "tipo": "SCA / deps", "comando": "trivy fs --severity HIGH,CRITICAL .",
        "criterio": "0 CVE HIGH/CRITICAL", "install": "https://aquasecurity.github.io/trivy",
    },
    "nuclei": {
        "tipo": "Dynamic scan", "comando": "nuclei -u <url> -t cves/",
        "criterio": "0 hallazgos HIGH/CRITICAL", "install": "https://github.com/projectdiscovery/nuclei",
    },
    "zap": {
        "tipo": "DAST", "comando": "zap-baseline.py -t <url>",
        "criterio": "0 alertas HIGH", "install": "https://www.zaproxy.org/download/",
    },
}

# ── Mapeo componente -> herramientas obligatorias ──────────────────────────────

COMPONENT_TOOLS = {
    "auth":   ["evol-scan", "evol-shield", "stride", "nuclei"],
    "api":    ["evol-scan", "evol-shield", "stride", "nuclei", "zap"],
    "db":     ["evol-scan", "evol-shield", "stride", "trivy"],
    "parser": ["evol-scan", "pruebas-fuzz", "evol-crash"],
    "input":  ["evol-scan", "pruebas-fuzz"],
    "ui":     ["evol-scan", "zap", "nuclei"],
    "binary": ["evol-crash", "pruebas-fuzz"],
    "deps":   ["trivy", "semgrep"],
}

# Herramientas que SIEMPRE aplican (cualquier codigo)
ALWAYS = ["evol-scan", "evol-shield"]


# ── deteccion de externas via doctor ───────────────────────────────────────────

def detect_external() -> dict[str, bool]:
    """Corre evol-doctor.sh --json, retorna {tool: instalado}."""
    result = {t: False for t in EXTERNAL_TOOLS}
    doctor = SCRIPT_DIR / "evol-doctor.sh"
    if not doctor.exists():
        return result
    try:
        out = subprocess.run(
            ["bash", str(doctor), "--json"],
            capture_output=True, text=True, timeout=30,
        ).stdout
        data = json.loads(out)
        checks = data.get("checks", []) if isinstance(data, dict) else []
        for c in checks:
            name = str(c.get("name", "")).lower()
            ok = str(c.get("status", "")).lower() in ("ok", "pass", "found")
            for tool in EXTERNAL_TOOLS:
                if tool in name and ok:
                    result[tool] = True
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        # Fallback: command -v directo
        import shutil
        for tool in EXTERNAL_TOOLS:
            cmd = "zap-baseline.py" if tool == "zap" else tool
            result[tool] = shutil.which(cmd) is not None
    return result


# ── generacion de checklist ────────────────────────────────────────────────────

def tools_for_components(components: list[str]) -> list[str]:
    """Herramientas obligatorias para los componentes dados + las SIEMPRE."""
    tools = list(ALWAYS)
    for comp in components:
        for t in COMPONENT_TOOLS.get(comp.strip().lower(), []):
            if t not in tools:
                tools.append(t)
    return tools


def gen_checklist(components: list[str], external_status: dict[str, bool]) -> str:
    """Bloque markdown de tareas STDD para los componentes."""
    tools = tools_for_components(components)
    lines = ["## Tests de seguridad (STDD) — arsenal por componente", ""]
    if components:
        lines.append(f"Componentes detectados: {', '.join(components)}")
        lines.append("")

    for t in tools:
        if t in NATIVE_TOOLS:
            info = NATIVE_TOOLS[t]
            lines.append(f"- [ ] {t} ({info['tipo']}): `{info['comando']}` -> {info['criterio']}")
        elif t in EXTERNAL_TOOLS:
            info = EXTERNAL_TOOLS[t]
            if external_status.get(t):
                lines.append(f"- [ ] {t} ({info['tipo']}): `{info['comando']}` -> {info['criterio']}")
            else:
                lines.append(f"- [ ] SKIP {t} ({info['tipo']}): no instalado. Instalar: {info['install']}")

    # Si algun componente es critico (auth/api), añadir pentest agentico
    if any(c.strip().lower() in ("auth", "api") for c in components):
        lines.append("- [ ] /advanced-agentic-pentesting (pentest agentico, sandbox) -> 0 exploits confirmados")
        lines.append("- [ ] Verificar exploit manualmente (Evol-DD sin auto-verify AGPL; usar nuclei POC o revision manual)")
    return "\n".join(lines) + "\n"


def gen_readme_section(external_status: dict[str, bool]) -> str:
    """Seccion README con TODO el arsenal (nativas + externas + estado)."""
    lines = [
        "## Herramientas de Seguridad",
        "",
        "Evol-DD incluye un arsenal de seguridad/pentest. Las NATIVAS corren sin instalar",
        "(Python stdlib). Las EXTERNAS son opt-in: si estan instaladas se usan, si no se",
        "marcan como skip. Documentado ANTES de instalar nada.",
        "",
        "### Nativas (incluidas — sin instalar)",
        "",
        "| Herramienta | Tipo | Comando | Detecta |",
        "|-------------|------|---------|---------|",
    ]
    for t, info in NATIVE_TOOLS.items():
        lines.append(f"| {t} | {info['tipo']} | `{info['comando']}` | {info['detecta']} |")

    lines += [
        "",
        "### Externas (opt-in — instalar para cobertura completa)",
        "",
        "| Herramienta | Tipo | Estado | Comando | Instalar |",
        "|-------------|------|--------|---------|----------|",
    ]
    for t, info in EXTERNAL_TOOLS.items():
        estado = "instalado" if external_status.get(t) else "FALTANTE"
        lines.append(f"| {t} | {info['tipo']} | {estado} | `{info['comando']}` | {info['install']} |")

    lines += [
        "",
        "### Mapeo componente -> herramientas obligatorias",
        "",
        "| Componente de la historia | Herramientas |",
        "|---------------------------|--------------|",
    ]
    for comp, tools in COMPONENT_TOOLS.items():
        lines.append(f"| {comp} | {', '.join(tools)} |")
    lines.append("")
    lines.append("Cualquier codigo: evol-scan + evol-shield (SIEMPRE).")
    return "\n".join(lines) + "\n"


# ── CLI ─────────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="evol-security-inventory", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("checklist", help="Genera bloque STDD para componentes")
    pc.add_argument("--components", default="", help="Lista separada por coma: auth,api,db,parser,ui,binary,deps")
    pc.add_argument("--format", default="md", choices=["md", "json"])

    pr = sub.add_parser("readme", help="Genera seccion README de herramientas")
    pr.add_argument("--write", default=None, help="Path al README a actualizar (in-place)")

    sub.add_parser("list", help="Lista arsenal completo")

    args = p.parse_args(argv)
    external = detect_external()

    if args.cmd == "checklist":
        components = [c for c in args.components.split(",") if c.strip()]
        if args.format == "json":
            tools = tools_for_components(components)
            print(json.dumps({"components": components, "tools": tools, "external": external}))
        else:
            print(gen_checklist(components, external))
        return 0

    if args.cmd == "readme":
        section = gen_readme_section(external)
        if args.write:
            readme = Path(args.write)
            content = readme.read_text(encoding="utf-8") if readme.exists() else ""
            marker = "## Herramientas de Seguridad"
            if marker in content:
                # Reemplazar seccion existente hasta el proximo H2 o EOF
                import re
                content = re.sub(
                    rf"{re.escape(marker)}.*?(?=^## |\Z)", section, content,
                    flags=re.DOTALL | re.MULTILINE,
                )
            else:
                content = content.rstrip() + "\n\n" + section
            readme.write_text(content, encoding="utf-8")
            print(f"[evol-security-inventory] seccion escrita en {args.write}")
        else:
            print(section)
        return 0

    if args.cmd == "list":
        print("=== NATIVAS (sin instalar) ===")
        for t, info in NATIVE_TOOLS.items():
            print(f"  {t}: {info['tipo']}")
        print("=== EXTERNAS (auto-discovery) ===")
        for t, info in EXTERNAL_TOOLS.items():
            estado = "instalado" if external.get(t) else "faltante"
            print(f"  {t}: {info['tipo']} [{estado}]")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
