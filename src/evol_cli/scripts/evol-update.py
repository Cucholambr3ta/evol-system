#!/usr/bin/env python3
"""evol-update — Mecanismo de actualizacion de Evol-DD.

Dos modos segun como este instalado el sistema:

  pip-mode (recomendado):
    evol-dd instalado via pip/pipx.
    Actualizar = pipx upgrade evol-dd o pip install --upgrade evol-dd.
    Luego re-propaga templates/workflows al proyecto activo.

  legacy-mode:
    Scripts copiados directamente al proyecto (evol-init --legacy).
    Requiere EVOL_SOURCE_DIR apuntando al repo fuente.
    Copia scripts actualizados + propaga workflows/templates.

Comandos:
  status   Version actual, modo instalacion, fuente
  check    Compara version instalada vs disponible (PyPI o fuente)
  apply    Aplica la actualizacion

Variables de entorno:
  EVOL_SOURCE_DIR   Ruta al repo fuente (legacy-mode)
  EVOL_PYPI_INDEX   URL indice PyPI (default: https://pypi.org/pypi)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib import request
from urllib.error import URLError


PYPI_INDEX = os.environ.get("EVOL_PYPI_INDEX", "https://pypi.org/pypi")
PACKAGE_NAME = "evol-dd"


def _current_version() -> str:
    try:
        from importlib.metadata import version
        return version(PACKAGE_NAME)
    except Exception:
        pass
    vf = Path(__file__).parent.parent / "VERSION"
    if vf.exists():
        return vf.read_text(encoding="utf-8").strip()
    return "0.0.0"


def _is_pip_install() -> bool:
    try:
        from importlib.metadata import distribution
        distribution(PACKAGE_NAME)
        return True
    except Exception:
        return False


def _is_pipx_install() -> bool:
    try:
        r = subprocess.run(["pipx", "list", "--short"], capture_output=True, text=True)
        return "evol-dd" in r.stdout or "evol_dd" in r.stdout
    except Exception:
        return False


def _latest_pypi_version() -> str | None:
    try:
        with request.urlopen(f"{PYPI_INDEX}/{PACKAGE_NAME}/json", timeout=10) as resp:
            return json.loads(resp.read())["info"]["version"]
    except Exception:
        return None


def _cmp(a: str, b: str) -> int:
    def parse(v):
        parts = []
        for p in v.replace("-", ".").split("."):
            try: parts.append(int(p))
            except ValueError: parts.append(p)
        return tuple(parts)
    x, y = parse(a), parse(b)
    return -1 if x < y else (1 if x > y else 0)


def _data_dir() -> Path:
    try:
        from evol_cli import _data_dir as _d
        return _d()
    except Exception:
        return Path(__file__).parent.parent


def _propagate(project_dir: Path, data: Path) -> None:
    print(f"[evol-update] Propagando al proyecto: {project_dir}")

    # Workflows SSoT
    src_wf = data / ".agent" / "workflows"
    dst_wf = project_dir / ".agent" / "workflows"
    if src_wf.is_dir() and dst_wf.is_dir():
        n = 0
        for wf in src_wf.glob("*.md"):
            shutil.copy2(wf, dst_wf / wf.name); n += 1
        print(f"[evol-update]   {n} workflows actualizados")

    # Templates (framework, no los del proyecto)
    src_tpl = data / "templates"
    dst_tpl = project_dir / "templates"
    if src_tpl.is_dir() and dst_tpl.is_dir():
        n = 0
        for ext in ("*.md", "*.yml", "*.yaml", "*.template"):
            for tpl in src_tpl.glob(ext):
                shutil.copy2(tpl, dst_tpl / tpl.name); n += 1
        print(f"[evol-update]   {n} templates actualizados")

    # Re-generar configs IDE
    adapt = project_dir / "scripts" / "evol-adapt.sh"
    if adapt.exists():
        subprocess.run(["bash", str(adapt), "all", f"--dest={project_dir}"],
                       capture_output=True)
        print(f"[evol-update]   configs IDE regeneradas via evol-adapt.sh all")

    print(f"[evol-update] Propagacion completa.")


def cmd_status(args) -> int:
    current = _current_version()
    pip = _is_pip_install()
    src = os.environ.get("EVOL_SOURCE_DIR", "no configurado")
    print(f"[evol-update] Version:  {current}")
    print(f"[evol-update] Modo:     {'pip' if pip else 'legacy'}")
    if pip:
        print(f"[evol-update] Upgrade:  pipx upgrade {PACKAGE_NAME}  (o pip install --upgrade)")
    else:
        print(f"[evol-update] Fuente:   {src}")
    return 0


def cmd_check(args) -> int:
    current = _current_version()
    pip = _is_pip_install()
    print(f"[evol-update] Version actual: {current}")

    if pip:
        print(f"[evol-update] Consultando PyPI...")
        latest = _latest_pypi_version()
        if latest is None:
            print(f"[evol-update] WARN: no se pudo contactar PyPI. Sin conexion?")
            return 1
        c = _cmp(current, latest)
        if c < 0:
            print(f"[evol-update] Actualizacion disponible: {current} → {latest}")
            print(f"[evol-update] Correr: evol update apply")
        elif c == 0:
            print(f"[evol-update] Sistema actualizado.")
        else:
            print(f"[evol-update] Version local ({current}) es mas reciente que PyPI ({latest}).")
    else:
        src = os.environ.get("EVOL_SOURCE_DIR")
        if not src:
            print(f"[evol-update] Setear EVOL_SOURCE_DIR=/ruta/repo/evol-dd")
            return 1
        vf = Path(src) / "VERSION"
        if vf.exists():
            sv = vf.read_text(encoding="utf-8").strip()
            c = _cmp(current, sv)
            if c < 0:
                print(f"[evol-update] Actualizacion disponible: {current} → {sv}")
            else:
                print(f"[evol-update] Sistema actualizado ({current}).")
        else:
            print(f"[evol-update] VERSION no encontrado en {src}")
            return 1
    return 0


def cmd_apply(args) -> int:
    current = _current_version()
    pip = _is_pip_install()
    project = Path(args.project)

    if pip:
        print(f"[evol-update] Actualizando paquete...")
        if _is_pipx_install():
            r = subprocess.run(["pipx", "upgrade", PACKAGE_NAME])
        else:
            r = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME])
        if r.returncode != 0:
            print(f"[evol-update] ERROR: fallo la actualizacion.", file=sys.stderr)
            return 1
        new = _current_version()
        print(f"[evol-update] Paquete: {current} → {new}")
        _propagate(project, _data_dir())
    else:
        src = os.environ.get("EVOL_SOURCE_DIR")
        if not src or not Path(src).exists():
            print(f"[evol-update] ERROR: EVOL_SOURCE_DIR no configurado o no existe.", file=sys.stderr)
            return 1
        source = Path(src)
        print(f"[evol-update] Actualizando desde: {source}")
        # Copiar scripts actualizados
        dst_scripts = project / "scripts"
        if dst_scripts.is_dir():
            n = 0
            for s in (source / "scripts").glob("evol-*.py"):
                shutil.copy2(s, dst_scripts / s.name); n += 1
            for s in (source / "scripts").glob("evol-*.sh"):
                shutil.copy2(s, dst_scripts / s.name); n += 1
            print(f"[evol-update]   {n} scripts copiados")
        _propagate(project, source)

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="evol-update", description=__doc__)
    p.add_argument("--project", default=os.getcwd())
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="Version y modo de instalacion")
    sub.add_parser("check",  help="Compara version vs disponible")
    sub.add_parser("apply",  help="Aplica la actualizacion")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return {"status": cmd_status, "check": cmd_check, "apply": cmd_apply}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
