#!/usr/bin/env python3
"""Evol-DD Compliance Auditor — Phase enforcement + lesson tracking + sprint reports."""
import sqlite3, os, sys, json, argparse, re
from datetime import datetime
from pathlib import Path
from _evol_common import get_state_db, get_logger, save_json, load_json, EXIT_OK, EXIT_BLOCKED, EXIT_ERROR

logger = get_logger("compliance")

PHASES = {
    "0.5": {"name": "Idea", "trigger": "/evol idea", "artefactos": ["acuerdos/idea/INDEX.md"], "gate": None},
    "0.7": {"name": "Discovery", "trigger": "/evol discovery", "artefactos": ["acuerdos/discovery/"], "gate": None},
    "1":   {"name": "Briefing", "trigger": "/evol briefing", "artefactos": ["acuerdos/idea/"], "gate": "briefing"},
    "2":   {"name": "Spec", "trigger": "/evol doc-granular", "artefactos": ["acuerdos/proyecto/"], "gate": "spec"},
    "3":   {"name": "Plan", "trigger": "/evol historias", "artefactos": ["acuerdos/historia-usuario-1/"], "gate": "plan"},
    "4":   {"name": "Build", "trigger": "/evol build", "artefactos": ["src/"], "gate": "build"},
    "5":   {"name": "QA", "trigger": "/evol qa", "artefactos": ["docs/qa/REPORTE_QA.md"], "gate": "qa"},
    "6":   {"name": "Retro", "trigger": "/evol retro", "artefactos": ["acuerdos/memoria/sprint-"], "gate": "retro"},
}

LESSON_PHASE_MAP = {
    "ARQUITECTURA": ["1", "2", "3"],
    "SEGURIDAD": ["3", "4", "5"],
    "DOMINIO": ["1", "2"],
    "TESTING": ["4", "5"],
    "DEVOPS": ["4", "5", "6"],
    "PROCESO": ["0.5", "0.7", "1", "2", "3", "4", "5", "6"],
    "HERRAMIENTAS": ["0.5", "0.7", "1", "2", "3", "4", "5", "6"],
}


def get_db():
    db_path = get_state_db()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _check_artifacts(phase):
    """Check if expected artifacts exist for a phase."""
    spec = PHASES.get(phase)
    if not spec:
        return {"ok": False, "reason": f"Unknown phase: {phase}"}

    found = []
    missing = []
    for art in spec["artefactos"]:
        if art.endswith("/"):
            if os.path.isdir(art):
                count = len(list(Path(art).glob("*.md")))
                found.append({"path": art, "type": "dir", "count": count})
            else:
                missing.append(art)
        else:
            if os.path.exists(art):
                found.append({"path": art, "type": "file"})
            else:
                missing.append(art)

    return {
        "ok": len(missing) == 0,
        "found": found,
        "missing": missing,
        "count": len(found),
    }


def _check_gate(phase):
    """Check if gate is signed for a phase."""
    spec = PHASES.get(phase)
    if not spec or not spec["gate"]:
        return {"signed": True, "reason": "No gate required"}

    gate_log = ".evol/.gate-log.jsonl"
    if not os.path.exists(gate_log):
        return {"signed": False, "reason": "No gate log found"}

    gate_name = spec["gate"]
    try:
        with open(gate_log) as f:
            for line in f:
                entry = json.loads(line)
                if entry.get("phase") == gate_name and entry.get("approved"):
                    return {"signed": True, "gate": gate_name}
    except Exception:
        pass

    return {"signed": False, "reason": f"Gate '{gate_name}' not signed"}


def _check_lessons_for_phase(phase):
    """Check pending lessons that apply to this phase."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("evol_lessons", os.path.join(os.path.dirname(__file__), "evol-lessons.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    lessons = mod.parse_lessons()
    relevant = []

    for lesson in lessons:
        if lesson.get("estado") != "pendiente":
            continue

        cats = LESSON_PHASE_MAP.get(lesson["category"], [])
        if phase in cats:
            relevant.append(lesson)

    return relevant


def _record_violation(conn, compliance_id, severity, rule, description, action_taken=""):
    """Record a violation in the log. Uses existing connection."""
    c = conn.cursor()
    c.execute("""
        INSERT INTO violation_log (compliance_id, severity, rule, description, action_taken)
        VALUES (?, ?, ?, ?, ?)
    """, (compliance_id, severity, rule, description, action_taken))


def cmd_check(args):
    """Pre-phase compliance check: artifacts + gate + lessons."""
    phase = args.fase
    sprint = args.sprint

    result = {
        "phase": phase,
        "phase_name": PHASES.get(phase, {}).get("name", "Unknown"),
        "timestamp": datetime.now().isoformat(),
        "verdict": "PASS",
        "checks": {},
    }

    artifact_check = _check_artifacts(phase)
    result["checks"]["artifacts"] = artifact_check

    gate_check = _check_gate(phase)
    result["checks"]["gate"] = gate_check

    lessons = _check_lessons_for_phase(phase)
    result["checks"]["lessons"] = {
        "pending_count": len(lessons),
        "lessons": [{"title": l["title"], "category": l["category"], "aplica": l["aplica"]} for l in lessons],
    }

    violations = 0

    if not artifact_check["ok"]:
        result["verdict"] = "BLOCK"
        result["block_reason"] = f"Missing artifacts: {', '.join(artifact_check['missing'])}"
        violations += 1

    if not gate_check["signed"]:
        result["verdict"] = "WARN" if result["verdict"] != "BLOCK" else result["verdict"]
        result["warnings"] = result.get("warnings", [])
        result["warnings"].append(f"Gate not signed: {gate_check['reason']}")
        violations += 1

    if lessons:
        has_critical = any(l["category"] in ["SEGURIDAD", "ARQUITECTURA"] for l in lessons)
        if has_critical:
            result["verdict"] = "BLOCK"
            result["block_reason"] = f"Critical lessons pending: {', '.join(l['title'] for l in lessons)}"
            violations += len(lessons)
        elif result["verdict"] != "BLOCK":
            result["verdict"] = "WARN"
            result["warnings"] = result.get("warnings", [])
            result["warnings"].append(f"{len(lessons)} pending lesson(s) apply to this phase")

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO phase_compliance (sprint, phase, artifacts_expected, artifacts_found,
            artifacts_count, gate_signed, violations, blocked, block_reason,
            lessons_pending)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sprint, phase,
        json.dumps(artifact_check.get("missing", [])),
        json.dumps([a["path"] for a in artifact_check.get("found", [])]),
        artifact_check.get("count", 0),
        gate_check["signed"],
        violations,
        result["verdict"] == "BLOCK",
        result.get("block_reason", ""),
        len(lessons),
    ))
    compliance_id = c.lastrowid

    if result["verdict"] == "BLOCK":
        _record_violation(conn, compliance_id, "CRITICAL", "phase-blocked",
                          result.get("block_reason", ""), "BLOCKED")

    conn.commit()
    conn.close()

    if args.json:
        print(json.dumps(result, indent=2))
        if result["verdict"] == "BLOCK":
            sys.exit(EXIT_BLOCKED)
    else:
        if result["verdict"] == "BLOCK":
            print(f"BLOCKED: {result.get('block_reason', 'Unknown')}")
            sys.exit(EXIT_BLOCKED)
        elif result["verdict"] == "WARN":
            for w in result.get("warnings", []):
                print(f"WARN: {w}")
            print(f"LESSONS_CHECK: {len(lessons)} pending lesson(s) apply to phase {phase}")
            for l in lessons:
                print(f"  - [{l['category']}] {l['title']}: {l['aplica']}")
        else:
            print(f"PASS: Phase {phase} ({PHASES.get(phase, {}).get('name', '')}) — artifacts OK, gate OK, no critical lessons pending")


def cmd_record(args):
    """Post-phase compliance record: record what happened."""
    phase = args.fase
    sprint = args.sprint
    agent = args.agent or "unknown"
    duration = args.duration

    artifact_check = _check_artifacts(phase)
    gate_check = _check_gate(phase)

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        UPDATE phase_compliance SET
            agent = ?,
            duration_seconds = ?
        WHERE id = (
            SELECT id FROM phase_compliance
            WHERE phase = ? AND sprint = ?
            ORDER BY id DESC LIMIT 1
        )
    """, (agent, duration, phase, sprint))
    conn.commit()
    conn.close()

    if args.json:
        print(json.dumps({"recorded": True, "phase": phase, "sprint": sprint, "agent": agent}))
    else:
        print(f"RECORDED: Phase {phase}, sprint {sprint}, agent {agent}")


def cmd_check_lessons(args):
    """Check which pending lessons apply to a phase or all phases."""
    phase = args.fase

    if phase:
        lessons = _check_lessons_for_phase(phase)
        result = {
            "phase": phase,
            "phase_name": PHASES.get(phase, {}).get("name", "Unknown"),
            "pendientes_total": len(lessons),
            "relevantes_fase": len(lessons),
            "lessons": [],
        }
        for l in lessons:
            result["lessons"].append({
                "title": l["title"],
                "category": l["category"],
                "estado": l.get("estado", "pendiente"),
                "aplica": l["aplica"],
                "leccion": l["leccion"][:150],
            })

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"LESSONS_CHECK: Phase {phase} ({result['phase_name']})")
            print(f"  Pendientes relevantes: {result['relevantes_fase']}")
            for l in result["lessons"]:
                print(f"  - [{l['category']}] {l['title']}")
                print(f"    Aplica a: {l['aplica']}")
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location("evol_lessons", os.path.join(os.path.dirname(__file__), "evol-lessons.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        all_lessons = mod.parse_lessons()
        pending = [l for l in all_lessons if l.get("estado") == "pendiente"]
        by_phase = {}
        for l in pending:
            cats = LESSON_PHASE_MAP.get(l["category"], [])
            for p in cats:
                by_phase.setdefault(p, []).append(l)

        result = {
            "pendientes_total": len(pending),
            "by_phase": {p: len(ls) for p, ls in by_phase.items()},
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Pendientes totales: {len(pending)}")
            for p in sorted(by_phase.keys()):
                print(f"  Phase {p} ({PHASES.get(p, {}).get('name', '')}): {len(by_phase[p])} lesson(s)")


def cmd_verify_applied(args):
    """Verify which pending lessons were actually applied in a sprint."""
    sprint = args.sprint
    import importlib.util
    spec = importlib.util.spec_from_file_location("evol_lessons", os.path.join(os.path.dirname(__file__), "evol-lessons.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    lessons = mod.parse_lessons()
    pending = [l for l in lessons if l.get("estado") == "pendiente"]

    applied = []
    still_pending = []

    for lesson in pending:
        evidence = _find_lesson_evidence(lesson, sprint)
        if evidence:
            applied.append({"title": lesson["title"], "evidence": evidence})
        else:
            still_pending.append(lesson)

    conn = get_db()
    c = conn.cursor()
    for a in applied:
        c.execute("""
            INSERT INTO lesson_tracking (lesson_title, sprint_verified, status, verified_at, evidence)
            VALUES (?, ?, 'aplicado', datetime('now'), ?)
        """, (a["title"], sprint, a["evidence"]))

    for s in still_pending:
        c.execute("""
            INSERT INTO lesson_tracking (lesson_title, sprint_verified, status, verified_at)
            VALUES (?, ?, 'pendiente', datetime('now'))
        """, (s["title"], sprint))

    conn.commit()
    conn.close()

    if args.json:
        print(json.dumps({
            "sprint": sprint,
            "applied": len(applied),
            "still_pending": len(still_pending),
            "details": [{"title": a["title"], "evidence": a["evidence"]} for a in applied],
        }, indent=2))
    else:
        print(f"VERIFY: Sprint {sprint}")
        print(f"  Applied: {len(applied)}")
        print(f"  Still pending: {len(still_pending)}")
        for a in applied:
            print(f"  [APLICADO] {a['title']}: {a['evidence']}")
        for s in still_pending:
            print(f"  [PENDIENTE] {s['title']}")


def _find_lesson_evidence(lesson, sprint):
    """Try to find evidence that a lesson was applied."""
    title_lower = lesson["title"].lower()
    keywords = re.findall(r'\w+', title_lower)
    keywords = [w for w in keywords if len(w) > 3]

    evidence_dirs = [
        f"acuerdos/lecciones/sprint-{sprint}.md",
        f"acuerdos/memoria/sprint-{sprint}.md",
        "lecciones.md",
    ]

    for evidence_file in evidence_dirs:
        if not os.path.exists(evidence_file):
            continue
        try:
            content = open(evidence_file).read().lower()
            if any(kw in content for kw in keywords if len(kw) > 4):
                return f"Pattern '{keywords[0] if keywords else ''}' found in {evidence_file}"
        except Exception:
            continue

    return None


def cmd_report(args):
    """Generate compliance report for a sprint."""
    sprint = args.sprint

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT * FROM phase_compliance WHERE sprint = ? ORDER BY id
    """, (sprint,))
    phases = [dict(r) for r in c.fetchall()]

    c.execute("""
        SELECT v.* FROM violation_log v
        JOIN phase_compliance p ON v.compliance_id = p.id
        WHERE p.sprint = ?
    """, (sprint,))
    violations = [dict(r) for r in c.fetchall()]

    c.execute("""
        SELECT * FROM lesson_tracking WHERE sprint_verified = ?
    """, (sprint,))
    lesson_status = [dict(r) for r in c.fetchall()]

    conn.close()

    total_phases = len(phases)
    blocked_phases = sum(1 for p in phases if p["blocked"])
    total_violations = len(violations)
    critical_violations = sum(1 for v in violations if v["severity"] == "CRITICAL")
    lessons_applied = sum(1 for l in lesson_status if l["status"] == "aplicado")
    lessons_pending = sum(1 for l in lesson_status if l["status"] == "pendiente")

    score = 100
    if total_phases > 0:
        score -= blocked_phases * 15
        score -= critical_violations * 10
        score -= (total_violations - critical_violations) * 3
        score = max(0, score)

    report = {
        "sprint": sprint,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "phases_total": total_phases,
            "phases_blocked": blocked_phases,
            "violations_total": total_violations,
            "violations_critical": critical_violations,
            "lessons_applied": lessons_applied,
            "lessons_pending": lessons_pending,
            "compliance_score": score,
        },
        "phases": phases,
        "violations": violations,
        "lesson_status": lesson_status,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  COMPLIANCE REPORT — Sprint {sprint}")
        print(f"{'='*60}")
        print(f"  Fases ejecutadas: {total_phases}")
        print(f"  Fases bloqueadas: {blocked_phases}")
        print(f"  Violaciones: {total_violations} ({critical_violations} CRITICAL)")
        print(f"  Lecciones aplicadas: {lessons_applied}")
        print(f"  Lecciones pendientes: {lessons_pending}")
        print(f"  Score de cumplimiento: {score}/100")
        print(f"{'='*60}\n")

        if phases:
            print("FASES:")
            for p in phases:
                status = "BLOCKED" if p["blocked"] else "OK"
                violations_str = f" ({p['violations']} violations)" if p["violations"] > 0 else ""
                print(f"  [{status}] Phase {p['phase']} ({p.get('agent', '?')}){violations_str}")
            print()

        if violations:
            print("VIOLACIONES:")
            for v in violations:
                print(f"  [{v['severity']}] {v['rule']}: {v['description']}")
            print()

        if lesson_status:
            print("LECCIONES:")
            for l in lesson_status:
                status = "[APLICADO]" if l["status"] == "aplicado" else "[PENDIENTE]"
                print(f"  {status} {l['lesson_title']}")
            print()

    report_path = f"acuerdos/auditoria/compliance-sprint-{sprint}.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    _write_report_md(report_path, report, phases, violations, lesson_status)

    if not args.json:
        print(f"Report written to: {report_path}")


def _write_report_md(path, report, phases, violations, lesson_status):
    """Write compliance report as markdown."""
    s = report["summary"]
    lines = [
        f"# Compliance Report — Sprint {report['sprint']}",
        f"",
        f"**Fecha:** {report['timestamp']}",
        f"**Score:** {s['compliance_score']}/100",
        f"",
        f"## Resumen",
        f"",
        f"| Metrica | Valor |",
        f"|---------|-------|",
        f"| Fases ejecutadas | {s['phases_total']} |",
        f"| Fases bloqueadas | {s['phases_blocked']} |",
        f"| Violaciones totales | {s['violations_total']} |",
        f"| Violaciones CRITICAL | {s['violations_critical']} |",
        f"| Lecciones aplicadas | {s['lessons_applied']} |",
        f"| Lecciones pendientes | {s['lessons_pending']} |",
        f"",
        f"## Fases",
        f"",
    ]

    if phases:
        lines.append("| Fase | Agente | Gate | Violations | Blocked |")
        lines.append("|------|--------|------|------------|---------|")
        for p in phases:
            gate = "SI" if p["gate_signed"] else "NO"
            blocked = "SI" if p["blocked"] else "NO"
            lines.append(f"| {p['phase']} | {p.get('agent', '-')} | {gate} | {p['violations']} | {blocked} |")
    else:
        lines.append("_(sin datos de fases)_")

    lines.extend(["", "## Violaciones", ""])

    if violations:
        lines.append("| Severidad | Regla | Descripcion | Accion |")
        lines.append("|-----------|-------|-------------|--------|")
        for v in violations:
            lines.append(f"| {v['severity']} | {v['rule']} | {v['description']} | {v.get('action_taken', '-')} |")
    else:
        lines.append("_(sin violaciones)_")

    lines.extend(["", "## Lecciones", ""])

    if lesson_status:
        lines.append("| Leccion | Estado | Evidencia |")
        lines.append("|---------|--------|-----------|")
        for l in lesson_status:
            status = "APLICADO" if l["status"] == "aplicado" else "PENDIENTE"
            lines.append(f"| {l['lesson_title']} | {status} | {l.get('evidence', '-')} |")
    else:
        lines.append("_(sin tracking de lecciones)_")

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Evol-DD Compliance Auditor")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("check", help="Pre-phase compliance check")
    p.add_argument("--fase", required=True, help="Phase number (0.5, 0.7, 1-6)")
    p.add_argument("--sprint", type=int, default=None)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("record", help="Post-phase compliance record")
    p.add_argument("--fase", required=True)
    p.add_argument("--sprint", type=int, default=None)
    p.add_argument("--agent", default=None)
    p.add_argument("--duration", type=float, default=None)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("check-lessons", help="Check pending lessons for phase")
    p.add_argument("--fase", default=None)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("verify-applied", help="Verify lessons applied in sprint")
    p.add_argument("--sprint", type=int, required=True)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("report", help="Generate compliance report for sprint")
    p.add_argument("--sprint", type=int, required=True)
    p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.cmd == "check":
        cmd_check(args)
    elif args.cmd == "record":
        cmd_record(args)
    elif args.cmd == "check-lessons":
        cmd_check_lessons(args)
    elif args.cmd == "verify-applied":
        cmd_verify_applied(args)
    elif args.cmd == "report":
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
