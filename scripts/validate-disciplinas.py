#!/usr/bin/env python3
"""validate-disciplinas.py — Validador del registro de disciplinas (Lote E).

Valida docs/disciplinas/ como registro de metodologias X-DD. Enforce la regla
transversal de DOC_STANDARD 1.7: toda ficha de disciplina cita fuentes con URL.

Para cada <ID>.md (excluye INDEX.md) verifica:
  - Existe su sidecar <ID>.json.
  - El sidecar tiene `fuentes[]` NO vacio (regla de citacion de fuentes).
  - Cada entrada de `fuentes[]` es una URL http/https resoluble en forma.
  - El .md contiene una seccion "Fuentes".
  - (--strict) El sidecar esta sincronizado con el .md (checksum) — sin drift.

Uso:
  python3 scripts/validate-disciplinas.py [--root docs/disciplinas] [--strict]
  python3 scripts/validate-disciplinas.py --help

Exit codes: 0 OK, 1 fallo de validacion, 2 error de uso.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_FUENTES_RE = re.compile(r"(?im)^#{1,4}\s*\d*\.?\s*fuentes\b")


def _checksum(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def validate(root: Path, strict: bool) -> list[str]:
    errors: list[str] = []
    md_files = sorted(p for p in root.glob("*.md") if p.stem != "INDEX")
    if not md_files:
        errors.append(f"{root}: no se encontraron fichas .md")
        return errors

    for md in md_files:
        sidecar = md.with_suffix(".json")
        content = md.read_text(encoding="utf-8", errors="replace")

        if not _FUENTES_RE.search(content):
            errors.append(f"{md.name}: falta seccion 'Fuentes' (DOC_STANDARD 1.7)")

        if not sidecar.exists():
            errors.append(f"{md.name}: falta sidecar {sidecar.name}")
            continue

        try:
            data = json.loads(sidecar.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{sidecar.name}: JSON invalido ({exc})")
            continue

        fuentes = data.get("fuentes", [])
        if not fuentes:
            errors.append(f"{sidecar.name}: fuentes[] vacio — ficha sin respaldo (DOC_STANDARD 1.7)")
        else:
            for url in fuentes:
                if not _URL_RE.match(str(url)):
                    errors.append(f"{sidecar.name}: fuente sin URL http(s) valida: {url!r}")

        if strict:
            expected = _checksum(content)
            actual = data.get("checksum_md")
            if actual != expected:
                errors.append(
                    f"{sidecar.name}: drift — checksum_md no coincide con {md.name} "
                    f"(corre: python3 scripts/evol-doc-sync.py sync-folder {root})"
                )

    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="validate-disciplinas")
    parser.add_argument("--root", default="docs/disciplinas", help="Carpeta del registro de disciplinas")
    parser.add_argument("--strict", action="store_true", help="Ademas valida sincronizacion sidecar (sin drift)")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"[validate-disciplinas] ERROR: no existe la carpeta {root}", file=sys.stderr)
        return 2

    errors = validate(root, args.strict)
    n = len([p for p in root.glob("*.md") if p.stem != "INDEX"])

    if errors:
        print(f"[validate-disciplinas] {len(errors)} error(es) en {n} fichas:")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    print(f"[validate-disciplinas] OK: {n} fichas validas, todas con fuentes[] no-vacio.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
