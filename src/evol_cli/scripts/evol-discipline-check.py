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


# ── Atomicidad — 1 doc = 1 dominio tecnico ────────────────────────────────────

_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "auth":         ["autenticacion", "authentication", "oauth", "jwt", "session", "login"],
    "db":           ["base de datos", "database", "schema", "migracion", "migration", "sql"],
    "api":          ["endpoint", "rest", "graphql", "openapi", "contrato de api"],
    "ui":           ["componente", "component", "wireframe", "frontend", "css", "html"],
    "security":     ["stride", "amenaza", "threat", "sast", "dast", "pentest"],
    "observability":["logging", "metrics", "alertas", "tracing", "slo", "sli"],
    "cicd":         ["pipeline", "deploy", "ci/cd", "github actions", "docker"],
    "testing":      ["test unitario", "unit test", "gherkin", "bdd", "coverage"],
    "domain_model": ["bounded context", "aggregate", "domain event", "ubiquitous language"],
}

_ALLOWED_MULTI_DOMAIN = {
    "INDEX.md", "README.md", "ONBOARDING.md", "RETROFIT_GUIDE.md",
    "X-DD_Integration_Guide.md",
}

_LINE_THRESHOLDS: dict[str, int] = {
    "ARQUITECTURA.md": 300,
    "DOMAIN.md":       250,
    "THREATS.md":      200,
    "GATE.md":         150,
    "constitucion.md": 200,
    "PLAN_QA.md":      200,
    "ONBOARDING.md":   200,
    "SPEC.md":         150,
    "FEATURES.md":     100,
}
_DEFAULT_MIN_LINES = 80


def check_atomicity(doc_path: Path) -> list[str]:
    """1 doc = 1 dominio tecnico. Doc con 4+ dominios en headings viola atomicidad."""
    if doc_path.name in _ALLOWED_MULTI_DOMAIN:
        return []
    content = _content(doc_path).lower()
    if not content:
        return []
    heading_text = " ".join(
        line.lstrip("#").strip()
        for line in content.splitlines()
        if line.startswith("#")
    )
    domains_present = [
        domain for domain, kwds in _DOMAIN_KEYWORDS.items()
        if any(kw in heading_text for kw in kwds)
    ]
    if len(domains_present) >= 4:
        return [
            f"ATOMICIDAD: {doc_path.name} menciona {len(domains_present)} dominios en headings "
            f"({', '.join(domains_present)}) — dividir en documentos separados (1 doc = 1 dominio)"
        ]
    return []


def check_min_lines(doc_path: Path) -> list[str]:
    """Umbral minimo de lineas segun DOC_STANDARD v2.0 seccion 1.5."""
    threshold = _LINE_THRESHOLDS.get(doc_path.name, _DEFAULT_MIN_LINES)
    if not doc_path.exists():
        return []
    lines = len(_content(doc_path).splitlines())
    if lines < threshold:
        return [
            f"PROFUNDIDAD: {doc_path.name} tiene {lines} lineas "
            f"(minimo {threshold} segun DOC_STANDARD v2.0)"
        ]
    return []


def check_doc_quality(root: Path, doc_path: Path) -> list[str]:
    """Atomicidad + umbral de lineas para un documento especifico."""
    return check_atomicity(doc_path) + check_min_lines(doc_path)


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
        print("[evol-discipline] EVOL_SKIP_DISCIPLINE=1 — checks omitidos.", file=sys.stderr)
        return []
    errors: list[str] = []
    for checker in PHASE_CHECKS.get(phase, []):
        errors.extend(checker(root))
    return errors


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="evol-discipline-check", description=__doc__)
    p.add_argument("phase", choices=list(PHASE_CHECKS.keys()) + ["doc"],
                   help="Fase a validar, o 'doc' para validar un documento especifico")
    p.add_argument("--root", default=".", help="Raiz del proyecto")
    p.add_argument("--doc", default=None, help="Path al documento (con phase=doc)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    root = Path(args.root).resolve()

    if args.phase == "doc" or args.doc:
        doc_path = Path(args.doc).resolve() if args.doc else None
        if doc_path is None:
            print("[evol-discipline] --doc requerido con phase=doc", file=sys.stderr)
            return 2
        errors = check_doc_quality(root, doc_path)
        if args.json:
            import json
            print(json.dumps({"doc": str(doc_path), "ok": not errors, "errors": errors}))
            return 0 if not errors else 1
        if errors:
            print(f"[evol-discipline] FALLO {doc_path.name}:")
            for e in errors:
                print(f"  - {e}")
            return 1
        print(f"[evol-discipline] OK {doc_path.name}: atomico y suficiente.")
        return 0

    errors = check_phase(root, args.phase)
    if args.json:
        import json
        print(json.dumps({"phase": args.phase, "ok": not errors, "errors": errors}))
        return 0 if not errors else 1
    if errors:
        print(f"[evol-discipline] FALLO {args.phase}: {len(errors)} violation(es):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"[evol-discipline] OK {args.phase}: contenido valido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
