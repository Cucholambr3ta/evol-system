#!/usr/bin/env python3
"""evol-openapi-merge — Mergea fragmentos OpenAPI por recurso en una raiz valida.

Caso monolitico-por-formato (ADR-0051): el tooling OpenAPI (Spectral, codegen, Prism)
necesita UNA raiz valida. Por eso openapi.yaml es generado, nunca editado a mano. Los
recursos se editan de forma atomica en api/openapi/fragments/<recurso>.yaml y se mergean.

Cada fragmento aporta sus `paths` y `components`. La raiz mergea todos + metadata
(openapi, info, servers) desde fragments/_root.yaml si existe, o defaults.

Comandos:
  merge --fragments <dir> --out <openapi.yaml>   Mergea fragmentos a raiz
  validate --root <openapi.yaml>                 Valida estructura minima OpenAPI 3.x

Stdlib + pyyaml (sin deps Node). Para swap a redocly/swagger-cli: ver ADR-0051.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[evol-openapi-merge] requiere pyyaml: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Merge recursivo: overlay gana en hojas, dicts se fusionan."""
    for k, v in overlay.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def merge_fragments(fragments_dir: Path, out_path: Path) -> dict:
    """Mergea todos los fragmentos .yaml en una raiz OpenAPI valida."""
    if not fragments_dir.is_dir():
        raise NotADirectoryError(f"{fragments_dir} no existe")

    # Metadata raiz: desde _root.yaml o defaults
    root_meta = fragments_dir / "_root.yaml"
    if root_meta.exists():
        root = yaml.safe_load(root_meta.read_text(encoding="utf-8")) or {}
    else:
        root = {
            "openapi": "3.0.3",
            "info": {"title": "API", "version": "1.0.0"},
            "paths": {},
            "components": {"schemas": {}},
        }

    root.setdefault("paths", {})
    root.setdefault("components", {}).setdefault("schemas", {})

    # Mergear cada fragmento (excepto _root.yaml)
    for frag in sorted(fragments_dir.glob("*.yaml")):
        if frag.name.startswith("_"):
            continue
        data = yaml.safe_load(frag.read_text(encoding="utf-8")) or {}
        if "paths" in data:
            _deep_merge(root["paths"], data["paths"])
        if "components" in data:
            _deep_merge(root["components"], data["components"])

    # Banner de generado (comentario YAML)
    banner = (
        "# GENERADO automaticamente por evol-openapi-merge.py (ADR-0051).\n"
        "# NO editar este archivo: editar api/openapi/fragments/<recurso>.yaml y re-mergear.\n"
    )
    out_path.write_text(banner + yaml.safe_dump(root, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return root


def validate_root(root_path: Path) -> list[str]:
    """Valida estructura minima OpenAPI 3.x."""
    errors = []
    if not root_path.exists():
        return [f"{root_path} no existe"]
    try:
        data = yaml.safe_load(root_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return [f"YAML invalido: {e}"]
    if not isinstance(data, dict):
        return ["raiz no es un objeto"]
    if not str(data.get("openapi", "")).startswith("3."):
        errors.append("falta 'openapi: 3.x'")
    if "info" not in data:
        errors.append("falta 'info'")
    if "paths" not in data:
        errors.append("falta 'paths'")
    return errors


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="evol-openapi-merge", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pm = sub.add_parser("merge", help="Mergea fragmentos a raiz")
    pm.add_argument("--fragments", required=True, help="Carpeta de fragmentos")
    pm.add_argument("--out", default="openapi.yaml", help="Raiz de salida")

    pv = sub.add_parser("validate", help="Valida estructura OpenAPI 3.x")
    pv.add_argument("--root", required=True, help="Raiz a validar")

    args = p.parse_args(argv)

    if args.cmd == "merge":
        root = merge_fragments(Path(args.fragments), Path(args.out))
        n_paths = len(root.get("paths", {}))
        print(f"[evol-openapi-merge] {n_paths} paths mergeados -> {args.out}")
        return 0

    if args.cmd == "validate":
        errors = validate_root(Path(args.root))
        if errors:
            print(f"[evol-openapi-merge] FALLO: {len(errors)} error(es):")
            for e in errors:
                print(f"  - {e}")
            return 1
        print(f"[evol-openapi-merge] OK: {args.root} es OpenAPI 3.x valido.")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
