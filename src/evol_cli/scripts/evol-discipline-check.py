#!/usr/bin/env python3
"""evol-discipline-check — Valida que cada artefacto cumple su disciplina -DD.

Cero deuda tecnica: el gate verifica CONTENIDO, no solo existencia.

Disciplinas y fases:
  briefing → SDD (SPEC.md) + FDD (FEATURES.md)
  spec     → DDD (DOMAIN.md) + Threat-Driven (THREATS.md)
  plan     → BDD/ATDD (*.feature)
  build    → TDD (tests/) + STDD (tests/security/)
  qa       → SecDD (QA_REPORT.md)

Activacion: EVOL_DISCIPLINE=1. Escape: EVOL_SKIP_DISCIPLINE=1.
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path


def _content(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _heading_present(content: str, *keywords: str) -> bool:
    for kw in keywords:
        if re.search(rf"(?im)^#{1,4}\s+.*{re.escape(kw)}", content):
            return True
    return False


# ── SDD ───────────────────────────────────────────────────────────────────────

def check_sdd(root: Path) -> list[str]:
    errors = []
    # evol-dd puede tener SPEC.md en .evol/briefing/ o en briefing/
    candidates = [
        root / ".evol" / "briefing" / "SPEC.md",
        root / "briefing" / "SPEC.md",
        root / ".xdd" / "briefing" / "SPEC.md",
    ]
    spec = next((p for p in candidates if p.exists()), None)
    if spec is None:
        return ["SDD: SPEC.md no encontrado (.evol/briefing/ o briefing/)"]
    content = _content(spec)
    if len(content.strip()) < 100:
        return ["SDD: SPEC.md tiene menos de 100 caracteres — contenido insuficiente"]

    required = [
        (["objetivo", "problema", "proposito", "resuelve"], "objetivo/problema"),
        (["alcance", "scope"], "alcance"),
        (["aceptacion", "acceptance", "criterio"], "criterios de aceptacion"),
        (["nfr", "no funcional", "rendimiento", "disponibilidad", "seguridad"], "NFRs"),
    ]
    for (kwds, label) in required:
        if not any(_heading_present(content, kw) or kw.lower() in content.lower() for kw in kwds):
            errors.append(f"SDD: SPEC.md falta seccion '{label}'")
    return errors


# ── FDD ───────────────────────────────────────────────────────────────────────

def check_fdd(root: Path) -> list[str]:
    errors = []
    candidates = [
        root / ".evol" / "briefing" / "FEATURES.md",
        root / "briefing" / "FEATURES.md",
        root / ".xdd" / "briefing" / "FEATURES.md",
    ]
    feat = next((p for p in candidates if p.exists()), None)
    if feat is None:
        return ["FDD: FEATURES.md no encontrado"]
    content = _content(feat)
    if len(content.strip()) < 50:
        return ["FDD: FEATURES.md tiene menos de 50 caracteres — catalogo vacio"]
    if not re.search(r"(?im)^#{2,4}\s+\w|^\s*[-*]\s+\w", content):
        errors.append("FDD: FEATURES.md no contiene features")
    if not re.search(r"(?i)must|should|could|won'?t|moscow|rice|prioridad|priority|alta|media|baja", content):
        errors.append("FDD: FEATURES.md no menciona priorizacion (MoSCoW, RICE, alta/media/baja)")
    return errors


# ── DDD ───────────────────────────────────────────────────────────────────────

def check_ddd(root: Path) -> list[str]:
    errors = []
    candidates = [
        root / ".evol" / "spec" / "DOMAIN.md",
        root / "spec" / "DOMAIN.md",
        root / ".xdd" / "spec" / "DOMAIN.md",
    ]
    domain = next((p for p in candidates if p.exists()), None)
    if domain is None:
        return ["DDD: DOMAIN.md no encontrado (.evol/spec/ o spec/)"]
    content = _content(domain)
    if len(content.strip()) < 100:
        return ["DDD: DOMAIN.md tiene menos de 100 caracteres — contenido insuficiente"]
    checks = [
        (["ubiquitous", "glosario", "vocabulario", "lenguaje"], "DDD: DOMAIN.md falta Ubiquitous Language o glosario"),
        (["bounded context", "contexto acotado"], "DDD: DOMAIN.md falta al menos 1 Bounded Context"),
        (["aggregate", "agregado"], "DDD: DOMAIN.md falta definicion de Aggregates"),
    ]
    for (kwds, msg) in checks:
        if not any(kw.lower() in content.lower() for kw in kwds):
            errors.append(msg)
    return errors


# ── Threat-Driven ─────────────────────────────────────────────────────────────

def check_threat_driven(root: Path) -> list[str]:
    errors = []
    candidates = [
        root / ".evol" / "spec" / "THREATS.md",
        root / "spec" / "THREATS.md",
        root / ".xdd" / "spec" / "THREATS.md",
    ]
    threats = next((p for p in candidates if p.exists()), None)
    if threats is None:
        return ["Threat-Driven: THREATS.md no encontrado"]
    content = _content(threats)
    if len(content.strip()) < 100:
        return ["Threat-Driven: THREATS.md tiene menos de 100 caracteres"]
    if not any(t.lower() in content.lower() for t in ["spoofing", "tampering", "stride"]):
        errors.append("Threat-Driven: THREATS.md no menciona STRIDE")
    if not re.search(r"(?i)(control|mitigacion|countermeasure|control propuesto)", content):
        errors.append("Threat-Driven: THREATS.md no documenta controles")
    return errors


# ── BDD/ATDD ──────────────────────────────────────────────────────────────────

def check_bdd(root: Path) -> list[str]:
    errors = []
    feature_files = list(root.rglob("*.feature"))
    if not feature_files:
        return []
    for fpath in feature_files:
        content = _content(fpath)
        scenarios = re.findall(r"(?im)^\s*Scenario[^:]*:", content)
        n = len(scenarios)
        if n == 0:
            errors.append(f"BDD: {fpath.name} no tiene ningun Scenario")
        elif n < 3:
            errors.append(f"BDD: {fpath.name} tiene {n} escenario(s) — minimo 3 (happy path + error + borde)")
        if not re.search(r"(?i)error|falla|fail|invalido|invalid|no autorizado", content):
            errors.append(f"BDD: {fpath.name} no tiene escenario de error")
    return errors


# ── TDD ───────────────────────────────────────────────────────────────────────

def check_tdd(root: Path) -> list[str]:
    unit_dir = root / "tests" / "unit"
    if unit_dir.is_dir():
        files = list(unit_dir.rglob("*.test.*")) + list(unit_dir.rglob("test_*.py"))
        if not files:
            return ["TDD: tests/unit/ existe pero no tiene archivos de test"]
        return []
    test_files = list(root.glob("tests/test_*.py")) + list(root.glob("tests/**/*.test.*"))
    if not test_files:
        return ["TDD: no se encontraron tests unitarios en tests/unit/ ni tests/test_*.py"]
    return []


# ── STDD ──────────────────────────────────────────────────────────────────────

def check_stdd(root: Path) -> list[str]:
    candidates = [
        root / ".evol" / "spec" / "THREATS.md",
        root / "spec" / "THREATS.md",
        root / ".xdd" / "spec" / "THREATS.md",
    ]
    threats = next((p for p in candidates if p.exists()), None)
    if threats is None:
        return []
    content = _content(threats)
    if not re.search(r"(?i)(spoofing|tampering|stride|amenaza|threat)", content):
        return []
    sec_files = []
    for d in [root / "tests" / "security", root / "tests" / "sec"]:
        if d.is_dir():
            sec_files.extend(d.rglob("*.security.*"))
            sec_files.extend(d.rglob("test_*security*"))
    if not sec_files:
        sec_files = list(root.glob("tests/**/*security*")) + list(root.glob("tests/**/*pentest*"))
    if not sec_files:
        return ["STDD: THREATS.md define amenazas pero no hay tests de seguridad en tests/security/"]
    return []


# ── SecDD ─────────────────────────────────────────────────────────────────────

def check_secdd(root: Path) -> list[str]:
    candidates = [
        root / ".evol" / "qa" / "QA_REPORT.md",
        root / "qa" / "QA_REPORT.md",
        root / ".xdd" / "qa" / "QA_REPORT.md",
    ]
    report = next((p for p in candidates if p.exists()), None)
    if report is None:
        return ["SecDD: QA_REPORT.md no encontrado (.evol/qa/ o qa/)"]
    content = _content(report)
    if len(content.strip()) < 50:
        return ["SecDD: QA_REPORT.md tiene menos de 50 caracteres"]
    errors = []
    for (kwds, msg) in [
        (["sast", "analisis estatico", "bandit", "semgrep"], "SecDD: falta SAST en QA_REPORT.md"),
        (["dast", "analisis dinamico", "zap", "burp"], "SecDD: falta DAST en QA_REPORT.md"),
        (["secrets", "gitleaks", "trufflehog"], "SecDD: falta secrets scanning en QA_REPORT.md"),
    ]:
        if not any(kw.lower() in content.lower() for kw in kwds):
            errors.append(msg)
    return errors


# ── Dispatcher ────────────────────────────────────────────────────────────────

PHASE_CHECKS: dict[str, list] = {
    "briefing": [check_sdd, check_fdd],
    "spec":     [check_ddd, check_threat_driven],
    "plan":     [check_bdd],
    "build":    [check_tdd, check_stdd],
    "qa":       [check_secdd],
    "retro":    [],
}


def check_phase(root: Path, phase: str) -> list[str]:
    if os.environ.get("EVOL_SKIP_DISCIPLINE") == "1":
        print(f"[evol-discipline] EVOL_SKIP_DISCIPLINE=1 — checks omitidos.", file=sys.stderr)
        return []
    errors: list[str] = []
    for checker in PHASE_CHECKS.get(phase, []):
        errors.extend(checker(root))
    return errors


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="evol-discipline-check", description=__doc__)
    p.add_argument("phase", choices=list(PHASE_CHECKS.keys()))
    p.add_argument("--root", default=".", help="Raiz del proyecto")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    errors = check_phase(root, args.phase)
    if args.json:
        import json
        print(json.dumps({"phase": args.phase, "ok": not errors, "errors": errors}))
        return 0 if not errors else 1
    if errors:
        print(f"[evol-discipline] ✗ {args.phase}: {len(errors)} violation(es):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"[evol-discipline] ✓ {args.phase}: contenido valido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
