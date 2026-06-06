#!/usr/bin/env python3
"""Evol-DD Lessons Engine — Lessons learned with continuous improvement."""
import os, sys, re, json, argparse
from datetime import datetime
from pathlib import Path
from _evol_common import get_logger, get_provider

logger = get_logger("lessons")

LESSONS_FILE = "lecciones.md"
CATEGORIES = ["ARQUITECTURA", "SEGURIDAD", "DOMINIO", "TESTING", "DEVOPS", "PROCESO", "HERRAMIENTAS"]

def jaccard_similarity(s1, s2):
    """Calculate Jaccard similarity (0.7 threshold for dedup)."""
    set1 = set(s1.lower().split())
    set2 = set(s2.lower().split())
    if not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)

def parse_lessons():
    """Parse lecciones.md and extract structured lessons."""
    if not os.path.exists(LESSONS_FILE):
        return []

    lessons = []
    with open(LESSONS_FILE) as f:
        content = f.read()

    pattern = r"### \[([A-Z]+)\] (.+?) — (\d{4}-\d{2}-\d{2})\n"
    matches = re.finditer(pattern, content)

    for m in matches:
        cat, title, date = m.groups()
        start = m.end()
        next_match = content.find("### [", start)
        end = next_match if next_match > 0 else len(content)

        lesson_text = content[start:end].strip()

        ctx = re.search(r"\*\*Contexto:\*\* (.+)", lesson_text)
        prob = re.search(r"\*\*Problema:\*\* (.+)", lesson_text)
        causa = re.search(r"\*\*Causa raiz:\*\* (.+)", lesson_text)
        leccion = re.search(r"\*\*Leccion:\*\* (.+)", lesson_text)
        aplica = re.search(r"\*\*Aplica a:\*\* (.+)", lesson_text)
        fix = re.search(r"\*\*Fix aplicado:\*\* (.+)", lesson_text)
        mejoras = re.search(r"\*\*Mejoras sugeridas:\*\* (.+)", lesson_text)
        estado = re.search(r"\*\*Estado mejoras:\*\* (.+)", lesson_text)

        lessons.append({
            "category": cat,
            "title": title,
            "date": date,
            "contexto": ctx.group(1) if ctx else "",
            "problema": prob.group(1) if prob else "",
            "causa": causa.group(1) if causa else "",
            "leccion": leccion.group(1) if leccion else "",
            "aplica": aplica.group(1) if aplica else "",
            "fix_aplicado": fix.group(1) if fix else "",
            "mejoras": mejoras.group(1) if mejoras else "",
            "estado": estado.group(1) if estado else "pendiente"
        })

    return lessons

def _lesson_to_md(lesson):
    """Serializa una leccion al formato markdown canonico."""
    lines = [
        f"\n### [{lesson['category']}] {lesson['title']} — {lesson['date']}",
        f"**Contexto:** {lesson['contexto']}",
        f"**Problema:** {lesson['problema']}",
        f"**Causa raiz:** {lesson['causa']}",
        f"**Leccion:** {lesson['leccion']}",
        f"**Aplica a:** {lesson['aplica']}",
    ]
    if lesson.get('fix_aplicado'):
        lines.append(f"**Fix aplicado:** {lesson['fix_aplicado']}")
    if lesson.get('mejoras'):
        lines.append(f"**Mejoras sugeridas:** {lesson['mejoras']}")
        lines.append(f"**Estado mejoras:** {lesson.get('estado', 'pendiente')}")
    return "\n".join(lines) + "\n"


def _insert_into_section(text, cat, lesson_md):
    """Inserta lesson_md dentro de la seccion ## CAT del archivo.

    Si la seccion existe: inserta al final de esa seccion (antes del siguiente ##).
    Si la seccion no existe: appenda al final del archivo.
    Elimina el placeholder '_(vacio)_' de la seccion si existe.
    """
    cat_header = f"## {cat}"
    if cat_header not in text:
        return text + lesson_md

    cat_pos = text.find(cat_header)
    after_header = cat_pos + len(cat_header)
    next_section = text.find("\n## ", after_header)
    section_end = next_section if next_section != -1 else len(text)

    section_body = text[after_header:section_end]

    # Eliminar placeholder
    section_body = section_body.replace("\n\n_(vacio)_\n", "")
    section_body = section_body.replace("\n_(vacio)_\n", "")

    # Insertar la leccion al final de la seccion
    new_section = section_body.rstrip() + lesson_md
    return text[:after_header] + new_section + text[section_end:]


def save_lessons(lessons):
    """Reescribe lecciones.md preservando la estructura de secciones por categoria.

    Si el archivo tiene secciones ## CATEGORIA, cada leccion va dentro de su seccion.
    Si no tiene secciones, reconstruye con cabecera estandar.
    """
    if not os.path.exists(LESSONS_FILE):
        _init_lessons_file(LESSONS_FILE)

    existing_text = open(LESSONS_FILE).read()
    has_sections = any(f"## {cat}" in existing_text for cat in CATEGORIES)

    if has_sections:
        # Modo estructura: preservar secciones, reescribir solo las lecciones
        # Reconstruir cada seccion con las lecciones de esa categoria
        # Primero extraer el header del archivo (hasta la primera seccion ##)
        first_section = min(
            (existing_text.find(f"## {cat}") for cat in CATEGORIES
             if f"## {cat}" in existing_text),
            default=-1
        )
        header = existing_text[:first_section] if first_section != -1 else existing_text

        # Reconstruir secciones
        result = header
        for cat in CATEGORIES:
            cat_lessons = [l for l in lessons if l["category"] == cat]
            result += f"## {cat}\n"
            if cat_lessons:
                for l in cat_lessons:
                    result += _lesson_to_md(l)
            else:
                result += "\n_(vacio)_\n"
            result += "\n"
        with open(LESSONS_FILE, "w") as f:
            f.write(result)
    else:
        # Modo legacy: reconstruir desde cero sin secciones
        with open(LESSONS_FILE, "w") as f:
            f.write("# lecciones.md — Aprendizajes Acumulados\n\n")
            f.write("> Sistema de gestion de lecciones con ciclo de mejora continua.\n")
            f.write("> Evol-DD aprende de cada sesion. Motor: scripts/evol-lessons.py\n\n")
            f.write("---\n\n## Lecciones\n")
            for lesson in lessons:
                f.write(_lesson_to_md(lesson))


def _init_lessons_file(path):
    """Crea lecciones.md con estructura de secciones por categoria."""
    with open(path, "w") as f:
        f.write("# lecciones.md — Aprendizajes Acumulados\n\n")
        f.write("> Lecciones aprendidas del proyecto. Motor: scripts/evol-lessons.py\n")
        f.write("> Buscar antes de decidir: evol-lessons search QUERY\n\n")
        f.write("---\n\n")
        for cat in CATEGORIES:
            f.write(f"## {cat}\n\n_(vacio)_\n\n")

def add_lesson(titulo, categoria, contexto, problema, causa, leccion, aplica, fix_aplicado=None):
    """Add new lesson with dedup check."""
    lessons = parse_lessons()

    for existing in lessons:
        similarity = jaccard_similarity(leccion, existing.get("leccion", ""))
        if similarity > 0.7:
            print(f"[WARN] Duplicate detected (similarity: {similarity:.2f})")
            print(f"[WARN] Existing: {existing['title']}")
            print(f"[WARN] New: {titulo}")

    new_lesson = {
        "category": categoria,
        "title": titulo,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "contexto": contexto,
        "problema": problema,
        "causa": causa,
        "leccion": leccion,
        "aplica": aplica,
        "fix_aplicado": fix_aplicado or "",
        "mejoras": "",
        "estado": "pendiente"
    }

    lessons.append(new_lesson)
    save_lessons(lessons)
    print(f"[OK] Lesson added: {titulo}")

def suggest_fix(title):
    """Call evol-researcher.py to suggest improvements."""
    provider = get_provider()

    lessons = parse_lessons()
    lesson = None
    for l in lessons:
        if l["title"] == title:
            lesson = l
            break

    if not lesson:
        print(f"[ERROR] Lesson not found: {title}")
        return

    prompt = f"""
Based on this lesson:
- Title: {lesson['title']}
- Problem: {lesson['problema']}
- Lesson: {lesson['leccion']}

Suggest concrete improvements to prevent this problem in the future.
Format: List 2-3 specific, actionable improvements.
"""

    if provider.__class__.__name__ == "MockProvider":
        improvements = "[mock — requires real LLM for actual suggestions]"
    else:
        result = provider.complete(prompt, max_tokens=500)
        improvements = result["content"]

    print(f"Suggested improvements for '{title}':")
    print(improvements)

    return improvements

def apply_fix(title, fix_description):
    """Mark improvements as applied."""
    lessons = parse_lessons()

    for lesson in lessons:
        if lesson["title"] == title:
            lesson["estado"] = "aplicado"
            lesson["mejoras"] = fix_description
            break

    save_lessons(lessons)
    print(f"[OK] Fix applied: {title}")

def search(query, max_results=5, categoria=None):
    """BM25-style search over lessons."""
    lessons = parse_lessons()
    results = []

    for lesson in lessons:
        if categoria and lesson["category"] != categoria:
            continue

        score = 0
        for term in query.lower().split():
            if term in lesson["leccion"].lower():
                score += 2
            if term in lesson["problema"].lower():
                score += 1
            if term in lesson["title"].lower():
                score += 1

        if score > 0:
            results.append((score, lesson))

    results.sort(key=lambda x: x[0], reverse=True)

    for i, (score, lesson) in enumerate(results[:max_results]):
        print(f"\n[{i+1}] [{lesson['category']}] {lesson['title']} — {lesson['date']}")
        print(f"    Leccion: {lesson['leccion'][:100]}...")
        if lesson.get("fix_aplicado"):
            print(f"    Fix: {lesson['fix_aplicado'][:100]}...")
        if lesson.get("mejoras") and lesson.get("estado") == "pendiente":
            print(f"    Mejoras pendientes: {lesson['mejoras'][:100]}...")

def list_lessons(categoria=None, pendientes_only=False, limit=None):
    """List lessons with filters."""
    lessons = parse_lessons()
    count = 0

    for lesson in lessons:
        if categoria and lesson["category"] != categoria:
            continue
        if pendientes_only and lesson.get("estado") != "pendiente":
            continue

        status = "[PENDIENTE]" if lesson.get("estado") == "pendiente" else "[APLICADO]"
        print(f"{status} [{lesson['category']}] {lesson['title']} — {lesson['date']}")
        count += 1

        if limit and count >= limit:
            break

    print(f"\n[INFO] Total: {count}")

def stats():
    """Show lessons statistics."""
    lessons = parse_lessons()

    total = len(lessons)
    print(f"Total lessons: {total}")

    by_cat = {}
    pendientes = 0
    aplicadas = 0

    for lesson in lessons:
        cat = lesson["category"]
        by_cat[cat] = by_cat.get(cat, 0) + 1

        if lesson.get("estado") == "pendiente":
            pendientes += 1
        elif lesson.get("estado") == "aplicado":
            aplicadas += 1

    print("\nBy category:")
    for cat, count in sorted(by_cat.items()):
        print(f"  {cat}: {count}")

    print(f"\nMejoras: {pendientes} pendientes, {aplicadas} aplicadas")

def gc():
    """Remove exact duplicates."""
    lessons = parse_lessons()
    seen = set()
    unique = []

    for lesson in lessons:
        key = (lesson["category"], lesson["title"], lesson["leccion"])
        if key not in seen:
            seen.add(key)
            unique.append(lesson)
        else:
            print(f"[GC] Removed duplicate: {lesson['title']}")

    if len(unique) < len(lessons):
        save_lessons(unique)
        print(f"[GC] Removed {len(lessons) - len(unique)} duplicates")

def extract(messages_file, auto=False):
    """Extract lesson candidates from JSONL session."""
    if not os.path.exists(messages_file):
        print(f"[ERROR] File not found: {messages_file}")
        return

    candidates = []

    with open(messages_file) as f:
        for line in f:
            msg = json.loads(line)
            content = msg.get("content", "")

            if any(kw in content.lower() for kw in ["error", "fail", "bug", "issue", "surprise"]):
                candidates.append({
                    "pattern": content[:200],
                    "timestamp": msg.get("timestamp", "")
                })

    print(f"[INFO] Found {len(candidates)} potential lesson candidates")

    if auto:
        for c in candidates[:3]:
            add_lesson(
                titulo=f"Extracted: {c['timestamp']}",
                categoria="PROCESO",
                contexto="Auto-extracted from session",
                problema=c["pattern"][:100],
                causa="Session analysis",
                leccion=c["pattern"][:200],
                aplica="Future sessions"
            )
    else:
        for c in candidates[:5]:
            print(f"  - {c['pattern'][:100]}...")

def verify_applied(sprint, as_json=False):
    """Verify which pending lessons were applied in a sprint.

    Checks if lesson keywords appear in sprint artifacts (lecciones, memoria).
    """
    import re as _re
    lessons = parse_lessons()
    pending = [l for l in lessons if l.get("estado") != "aplicado"]

    applied = []
    still_pending = []

    evidence_dirs = [
        f"acuerdos/lecciones/sprint-{sprint}.md",
        f"acuerdos/memoria/sprint-{sprint}.md",
    ]

    for lesson in pending:
        title_lower = lesson["title"].lower()
        keywords = [w for w in _re.findall(r'\w+', title_lower) if len(w) > 4]

        found_evidence = None
        for evidence_file in evidence_dirs:
            if not os.path.exists(evidence_file):
                continue
            try:
                content = open(evidence_file).read().lower()
                if any(kw in content for kw in keywords):
                    found_evidence = f"Keyword '{keywords[0]}' found in {evidence_file}"
                    break
            except Exception:
                continue

        if found_evidence:
            applied.append({"title": lesson["title"], "category": lesson["category"], "evidence": found_evidence})
        else:
            still_pending.append(lesson)

    if as_json:
        print(json.dumps({
            "sprint": sprint,
            "applied": len(applied),
            "still_pending": len(still_pending),
            "details": applied,
        }, indent=2))
    else:
        print(f"VERIFY APPLIED — Sprint {sprint}")
        print(f"  Aplicadas: {len(applied)}")
        print(f"  Pendientes: {len(still_pending)}")
        if applied:
            print("\n  APLICADAS:")
            for a in applied:
                print(f"    [{a['category']}] {a['title']}")
                print(f"      Evidencia: {a['evidence']}")
        if still_pending:
            print("\n  PENDIENTES:")
            for s in still_pending:
                print(f"    [{s['category']}] {s['title']}")

    return {"applied": applied, "pending": still_pending}


def main():
    parser = argparse.ArgumentParser(description="Evol-DD Lessons Engine")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("add", help="Add lesson")
    p.add_argument("--titulo", required=True)
    p.add_argument("--categoria", required=True, choices=CATEGORIES)
    p.add_argument("--contexto", required=True)
    p.add_argument("--problema", required=True)
    p.add_argument("--causa", required=True)
    p.add_argument("--leccion", required=True)
    p.add_argument("--aplica", required=True)
    p.add_argument("--fix-aplicado", default=None)

    p = sub.add_parser("suggest-fix", help="Suggest improvements for lesson")
    p.add_argument("titulo")
    p.add_argument("--apply", action="store_true")

    p = sub.add_parser("apply-fix", help="Mark improvements as applied")
    p.add_argument("titulo")
    p.add_argument("--fix", required=True)

    p = sub.add_parser("search", help="Search lessons")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=5)
    p.add_argument("--categoria", choices=CATEGORIES)

    p = sub.add_parser("suggest", help="Get lessons for context")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=3)

    p = sub.add_parser("list", help="List lessons")
    p.add_argument("--categoria", choices=CATEGORIES)
    p.add_argument("--pendientes", action="store_true")
    p.add_argument("--limit", type=int)

    sub.add_parser("stats", help="Show statistics")
    sub.add_parser("gc", help="Remove duplicates")

    p = sub.add_parser("extract", help="Extract from JSONL")
    p.add_argument("--messages", required=True)
    p.add_argument("--auto", action="store_true")

    p = sub.add_parser("verify-applied", help="Verify which pending lessons were applied in a sprint")
    p.add_argument("--sprint", type=int, required=True)
    p.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.cmd == "add":
        add_lesson(
            args.titulo, args.categoria, args.contexto,
            args.problema, args.causa, args.leccion, args.aplica, args.fix_aplicado
        )
    elif args.cmd == "suggest-fix":
        improvements = suggest_fix(args.titulo)
        if args.apply and improvements:
            pass
    elif args.cmd == "apply-fix":
        apply_fix(args.titulo, args.fix)
    elif args.cmd == "search":
        search(args.query, args.max, args.categoria)
    elif args.cmd == "suggest":
        search(args.query, args.max)
    elif args.cmd == "list":
        list_lessons(args.categoria, args.pendientes, args.limit)
    elif args.cmd == "stats":
        stats()
    elif args.cmd == "gc":
        gc()
    elif args.cmd == "extract":
        extract(args.messages, args.auto)
    elif args.cmd == "verify-applied":
        verify_applied(args.sprint, args.json)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()