#!/usr/bin/env python3
"""evol-doc-sync — Genera sidecar JSON compacto desde documentos Markdown.

Motor del ahorro de tokens del pipeline atomico Evol-DD. El MD es la fuente de verdad
(calidad completa). El JSON es la estructura maxima de ahorro: un agente lee el JSON
(~300 tokens) para mapear que existe y donde, y solo carga el MD completo (~2500 tokens)
del subdominio que va a implementar. Ahorro ~95% en navegacion.

Contrato del JSON sidecar (<nombre>.json junto a <nombre>.md):
  doc, dominio, subdominio, resumen, secciones, entidades, trazabilidad,
  fuentes, tokens_md, tokens_json, lineas, checksum_md, actualizado

El campo `fuentes` captura las URLs citadas en la seccion "Fuentes" del MD. Regla Evol-DD:
todo documento producto de investigacion web debe citar la URL de la fuente (DOC_STANDARD).
`fuentes` permite al validador exigir respaldo no-vacio en docs de disciplina/investigacion.

Comandos:
  sync --doc <path.md>        Genera/actualiza el .json de un documento
  sync-folder <carpeta>       Regenera todos los .json + INDEX.json de la carpeta
  sync-all <raiz>             Regenera todo el arbol + INDEX.json maestro
  verify <carpeta>            Detecta drift (MD cambio sin re-sync)

Activacion: opt-in via EVOL_DOC_SYNC=1 en el hook, o llamado directo desde workflows.
MD = fuente de verdad. Si .json existe pero checksum_md no coincide, regenera.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# ── token estimation (reusa evol-context.py si esta disponible) ─────────────────

def _estimate_tokens(text: str) -> int:
    """Reusa estimate_tokens de evol-context.py; fallback a heuristica local."""
    if not text:
        return 0
    try:
        import importlib.util
        ctx = Path(__file__).parent / "evol-context.py"
        if ctx.exists():
            spec = importlib.util.spec_from_file_location("evol_context", ctx)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.estimate_tokens(text)
    except Exception:
        pass
    # Heuristica local: ~4 chars/token
    char_count = len(text)
    word_count = len(re.findall(r"\S+", text))
    return int(((char_count / 4.0) + (word_count * 1.3)) / 2)


# ── parseo del MD ──────────────────────────────────────────────────────────────

def _checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def _extract_summary(content: str) -> str:
    """Resumen: primera linea no-vacia tras el titulo H1 que declara fronteras.

    Convencion doc-granular: la primera linea tras el titulo declara que cubre
    y que NO cubre (linea con '>' o parrafo de fronteras).
    """
    lines = content.splitlines()
    seen_h1 = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            seen_h1 = True
            continue
        if seen_h1 and stripped:
            # Quitar prefijo de blockquote
            text = stripped.lstrip(">").strip()
            if text and not text.startswith("#"):
                return text[:200]
    return ""


def _extract_sections(content: str) -> list[str]:
    """Slugs de los headings H2 (secciones principales)."""
    sections = []
    for line in content.splitlines():
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            # Quitar numeracion "## 3. Schemas" → "schemas"
            title = re.sub(r"^\d+\.?\s*", "", m.group(1).strip())
            sections.append(_slugify(title))
    return sections


def _extract_entities(content: str) -> list[str]:
    """Entidades de bloques de codigo SQL/schema: nombres de tablas/tipos/interfaces."""
    entities = set()
    # SQL: CREATE TABLE x
    for m in re.finditer(r"(?i)create\s+table\s+(?:if\s+not\s+exists\s+)?[`\"']?(\w+)", content):
        entities.add(m.group(1).lower())
    # TypeScript/Zod: interface X, type X, const X = z.object
    for m in re.finditer(r"(?:interface|type)\s+(\w+)", content):
        entities.add(m.group(1).lower())
    # entradas de tabla markdown que parecen entidades (primera columna capitalizada)
    return sorted(entities)[:20]


def _extract_traceability(content: str) -> dict:
    """Seccion de trazabilidad: origen (briefing) + relacionados (otros docs)."""
    trace = {"origen": [], "relacionados": []}
    # Buscar seccion de trazabilidad
    m = re.search(r"(?is)^#{1,4}\s*\d*\.?\s*trazabilidad.*?$(.*?)(?=^#{1,4}\s|\Z)", content, re.MULTILINE)
    if not m:
        return trace
    block = m.group(1)
    # Referencias a .md
    for ref in re.findall(r"([\w\-/]+\.md)", block):
        if "briefing" in ref.lower() or ref in (
            "stack.md", "arquitectura.md", "auth.md", "seguridad.md", "producto.md",
            "usuarios.md", "integraciones.md", "datos-privacidad.md", "observabilidad.md",
        ):
            if ref not in trace["origen"]:
                trace["origen"].append(ref)
        else:
            if ref not in trace["relacionados"]:
                trace["relacionados"].append(ref)
    return trace


def _extract_sources(content: str) -> list[str]:
    """URLs citadas en la seccion 'Fuentes'. Regla DOC_STANDARD: investigacion web cita su link.

    Devuelve la lista de URLs (http/https) que aparecen bajo un encabezado 'Fuentes'.
    Documento de investigacion sin fuentes => lista vacia => el validador lo marca INCOMPLETO.
    """
    m = re.search(
        r"(?is)^#{1,4}\s*\d*\.?\s*fuentes.*?$(.*?)(?=^#{1,4}\s|\Z)", content, re.MULTILINE
    )
    if not m:
        return []
    block = m.group(1)
    urls: list[str] = []
    for url in re.findall(r"https?://[^\s\)\]\}<>\"']+", block):
        url = url.rstrip(".,;")
        if url not in urls:
            urls.append(url)
    return urls


def _domain_subdomain(doc_path: Path, root: Path | None = None) -> tuple[str, str]:
    """Deriva dominio (carpeta padre) y subdominio (nombre archivo sin ext)."""
    subdominio = doc_path.stem
    dominio = doc_path.parent.name
    return dominio, subdominio


# ── generacion del sidecar JSON ────────────────────────────────────────────────

def build_sidecar(doc_path: Path) -> dict:
    """Construye el dict del sidecar JSON desde un MD."""
    content = doc_path.read_text(encoding="utf-8", errors="replace")
    dominio, subdominio = _domain_subdomain(doc_path)
    sections = _extract_sections(content)
    summary = _extract_summary(content)
    entities = _extract_entities(content)
    trace = _extract_traceability(content)
    fuentes = _extract_sources(content)
    tokens_md = _estimate_tokens(content)
    lineas = len(content.splitlines())

    sidecar = {
        "doc": doc_path.name,
        "dominio": dominio,
        "subdominio": subdominio,
        "resumen": summary,
        "secciones": sections,
        "entidades": entities,
        "trazabilidad": trace,
        "fuentes": fuentes,
        "tokens_md": tokens_md,
        "lineas": lineas,
        "checksum_md": _checksum(content),
        "actualizado": _now(),
    }
    # tokens_json se calcula sobre el JSON serializado
    json_str = json.dumps(sidecar, ensure_ascii=False)
    sidecar["tokens_json"] = _estimate_tokens(json_str)
    return sidecar


def sync_doc(doc_path: Path, force: bool = False) -> bool:
    """Genera/actualiza el .json de un doc. Retorna True si escribio."""
    if not doc_path.exists() or doc_path.suffix != ".md":
        return False
    if doc_path.name in ("INDEX.md",):
        return False  # INDEX.md tiene su propio INDEX.json generado por sync-folder

    json_path = doc_path.with_suffix(".json")
    content = doc_path.read_text(encoding="utf-8", errors="replace")
    current_checksum = _checksum(content)

    # Skip si el JSON existe y el checksum coincide (no drift)
    if json_path.exists() and not force:
        try:
            existing = json.loads(json_path.read_text(encoding="utf-8"))
            if existing.get("checksum_md") == current_checksum:
                return False
        except (json.JSONDecodeError, OSError):
            pass

    sidecar = build_sidecar(doc_path)
    json_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def sync_folder(folder: Path) -> dict:
    """Regenera .json de todos los docs + INDEX.json de la carpeta."""
    if not folder.is_dir():
        raise NotADirectoryError(f"{folder} no es una carpeta")

    docs = []
    for md in sorted(folder.glob("*.md")):
        if md.name == "INDEX.md":
            continue
        sync_doc(md)
        json_path = md.with_suffix(".json")
        if json_path.exists():
            docs.append(json.loads(json_path.read_text(encoding="utf-8")))

    index = {
        "dominio": folder.name,
        "docs": [
            {
                "subdominio": d["subdominio"],
                "doc": d["doc"],
                "resumen": d["resumen"],
                "tokens_md": d["tokens_md"],
                "entidades": d.get("entidades", []),
            }
            for d in docs
        ],
        "total_docs": len(docs),
        "total_tokens_md": sum(d["tokens_md"] for d in docs),
        "actualizado": _now(),
    }
    index_str = json.dumps(index, ensure_ascii=False)
    index["total_tokens_json"] = _estimate_tokens(index_str)

    index_path = folder / "INDEX.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return index


def sync_all(root: Path) -> dict:
    """Regenera todo el arbol + INDEX.json maestro."""
    if not root.is_dir():
        raise NotADirectoryError(f"{root} no es una carpeta")

    domains = []
    # Cada subcarpeta directa es un dominio
    for sub in sorted(root.iterdir()):
        if sub.is_dir():
            idx = sync_folder(sub)
            domains.append({
                "dominio": idx["dominio"],
                "total_docs": idx["total_docs"],
                "total_tokens_md": idx["total_tokens_md"],
            })

    # Docs directamente en root (sin subcarpeta)
    root_docs = [m for m in root.glob("*.md") if m.name != "INDEX.md"]
    for md in root_docs:
        sync_doc(md)

    master = {
        "raiz": str(root.name),
        "dominios": domains,
        "total_dominios": len(domains),
        "total_docs": sum(d["total_docs"] for d in domains),
        "total_tokens_md": sum(d["total_tokens_md"] for d in domains),
        "actualizado": _now(),
    }
    master_str = json.dumps(master, ensure_ascii=False)
    master["total_tokens_json"] = _estimate_tokens(master_str)

    master_path = root / "INDEX.json"
    master_path.write_text(json.dumps(master, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return master


def verify(folder: Path) -> list[str]:
    """Detecta drift: MD sin .json, o .json con checksum desactualizado."""
    errors = []
    for md in sorted(folder.rglob("*.md")):
        if md.name == "INDEX.md":
            continue
        json_path = md.with_suffix(".json")
        if not json_path.exists():
            errors.append(f"DRIFT: {md.name} no tiene sidecar .json")
            continue
        try:
            sidecar = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            errors.append(f"DRIFT: {json_path.name} no es JSON valido")
            continue
        current = _checksum(md.read_text(encoding="utf-8", errors="replace"))
        if sidecar.get("checksum_md") != current:
            errors.append(
                f"DRIFT: {md.name} cambio sin re-sync "
                f"(json={sidecar.get('checksum_md', '?')[:8]} actual={current[:8]})"
            )
    return errors


# ── CLI ─────────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="evol-doc-sync", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("sync", help="Genera/actualiza el .json de un documento")
    ps.add_argument("--doc", required=True, help="Path al documento .md")
    ps.add_argument("--force", action="store_true", help="Regenerar aunque el checksum coincida")

    pf = sub.add_parser("sync-folder", help="Regenera .json + INDEX.json de la carpeta")
    pf.add_argument("folder", help="Carpeta a sincronizar")

    pa = sub.add_parser("sync-all", help="Regenera todo el arbol + INDEX.json maestro")
    pa.add_argument("root", help="Raiz a sincronizar")

    pv = sub.add_parser("verify", help="Detecta drift (MD cambio sin re-sync)")
    pv.add_argument("folder", help="Carpeta a verificar")
    pv.add_argument("--json", action="store_true", help="Salida JSON")

    args = p.parse_args(argv)

    if args.cmd == "sync":
        wrote = sync_doc(Path(args.doc), force=args.force)
        print(f"[evol-doc-sync] {'escrito' if wrote else 'sin cambios'}: {Path(args.doc).with_suffix('.json').name}")
        return 0

    if args.cmd == "sync-folder":
        idx = sync_folder(Path(args.folder))
        print(f"[evol-doc-sync] {idx['total_docs']} docs, {idx['total_tokens_md']} tokens MD -> "
              f"INDEX.json {idx['total_tokens_json']} tokens")
        return 0

    if args.cmd == "sync-all":
        master = sync_all(Path(args.root))
        print(f"[evol-doc-sync] {master['total_dominios']} dominios, {master['total_docs']} docs, "
              f"{master['total_tokens_md']} tokens MD -> maestro {master['total_tokens_json']} tokens")
        return 0

    if args.cmd == "verify":
        errors = verify(Path(args.folder))
        if args.json:
            print(json.dumps({"ok": not errors, "errors": errors}))
            return 0 if not errors else 1
        if errors:
            print(f"[evol-doc-sync] {len(errors)} drift(s):")
            for e in errors:
                print(f"  - {e}")
            return 1
        print("[evol-doc-sync] OK: sin drift, todos los .json sincronizados.")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
