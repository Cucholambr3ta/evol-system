"""evol_cli — Entry-point dispatcher para Evol-DD.

NO reescribe los scripts (patron ADR-0008 de X-DD: consolidacion CLI diferida).
Cada entry-point es un dispatcher fino que ejecuta el script correspondiente.

Resolucion de paths (mismo patron que xdd_cli — fix aprendido de X-DD):
  1. EVOL_SCRIPTS_DIR / EVOL_DATA_DIR si estan seteados.
  2. Instalacion editable: directorio junto al repo (../../scripts desde src/evol_cli).
  3. Data del wheel: directorio empaquetado dentro del paquete (evol_cli/<dir>).

Bug historico corregido preventivamente: pyproject.toml empaqueta TODOS los
data dirs (manifests/, templates/, .agent/, skills/, docs/, VERSION) para que
evol --version y evol init --list-profiles funcionen en instalacion pipx/wheel.
"""
from __future__ import annotations

import os
import runpy
import subprocess
import sys
from pathlib import Path


def _resolve_version() -> str:
    try:
        from importlib.metadata import PackageNotFoundError, version
        return version("evol-dd")
    except (ImportError, Exception):
        pass
    # Fallback: leer VERSION desde data dir
    try:
        return (_data_dir() / "VERSION").read_text(encoding="utf-8").strip()
    except Exception:
        return "0.1.0-dev"


def _scripts_dir() -> Path:
    """Resuelve el directorio scripts/ con logica de 3 niveles."""
    env = os.environ.get("EVOL_SCRIPTS_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent
    # editable: repo_root/src/evol_cli → repo_root/scripts
    repo_scripts = here.parent.parent / "scripts"
    if repo_scripts.is_dir():
        return repo_scripts
    # wheel: scripts empaquetado como data dentro del paquete
    bundled = here / "scripts"
    if bundled.is_dir():
        return bundled
    raise FileNotFoundError(
        "No encuentro scripts/ Evol-DD. Setea EVOL_SCRIPTS_DIR al directorio scripts/."
    )


def _data_dir() -> Path:
    """Raiz de los data dirs (manifests/, templates/, .agent/, skills/, docs/, VERSION).

    Misma logica de 3 niveles que _scripts_dir().
    Los scripts bash reciben esta ruta como EVOL_DATA_DIR para no depender de
    dirname(BASH_SOURCE) relativo, que rompe en instalaciones pipx/wheel.
    """
    env = os.environ.get("EVOL_DATA_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent
    # editable: repo_root/src/evol_cli → repo_root/
    repo_root = here.parent.parent
    if (repo_root / "manifests").is_dir():
        return repo_root
    # wheel: data empaquetado dentro del paquete (evol_cli/ contiene manifests/, etc.)
    if (here / "manifests").is_dir():
        return here
    return here


__version__ = _resolve_version()

SCRIPTS = {
    "gate":        "evol-gate.py",
    "eval":        "evol-eval.py",
    "flow":        "evol-flow.py",
    "provider":    "evol-provider.py",
    "shield":      "evol-shield.py",
    "orchestrate": "evol-orchestrate.py",
    "agent":       "evol-agent-lifecycle.py",
    "evolve":      "evol-evolve.py",
    "research":    "evol-researcher.py",
    "memory":      "evol-memory.py",
    "lessons":     "evol-lessons.py",
    "update":      "evol-update.py",
}

SHELL_SCRIPTS = {
    "init":           "evol-init.sh",
    "start":          "evol-start.sh",
    "adapt":          "evol-adapt.sh",
    "doctor":         "evol-doctor.sh",
    "brand":          "evol-brand.sh",
    "global-install": "evol-global-install.sh",
}


def _run(script_name: str) -> int:
    script = _scripts_dir() / script_name
    if not script.exists():
        print(f"[evol] script no encontrado: {script}", file=sys.stderr)
        return 2
    sys.argv = [str(script)] + sys.argv[1:]
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else (0 if e.code is None else 1)
    return 0


def _run_shell(script_name: str, args: list[str]) -> int:
    """Ejecuta un script .sh con bash, inyectando EVOL_DATA_DIR."""
    script = _scripts_dir() / script_name
    if not script.exists():
        print(f"[evol] script no encontrado: {script}", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env.setdefault("EVOL_DATA_DIR", str(_data_dir()))
    return subprocess.call(["bash", str(script), *args], env=env)


def _usage() -> None:
    print(f"evol {__version__} — Evol-DD CLI")
    print("\nComandos Python:")
    for name in sorted(SCRIPTS):
        print(f"  {name}")
    print("\nComandos Bash:")
    for name in sorted(SHELL_SCRIPTS):
        print(f"  {name}")
    print("\nEj: evol gate status · evol init /mi-proyecto · evol doctor")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        _usage()
        return 0
    if argv[0] in ("-v", "--version"):
        print(f"evol-dd {__version__}")
        return 0
    sub, rest = argv[0], argv[1:]
    if sub == "install-global":
        return install_global()
    if sub in SCRIPTS:
        sys.argv = [SCRIPTS[sub]] + rest
        return _run(SCRIPTS[sub])
    if sub in SHELL_SCRIPTS:
        return _run_shell(SHELL_SCRIPTS[sub], rest)
    print(f"[evol] subcomando desconocido: {sub!r}", file=sys.stderr)
    _usage()
    return 2


# Entry-points individuales
def gate():        sys.argv = ["evol-gate"] + sys.argv[2:]; _run(SCRIPTS["gate"])
def eval_():       sys.argv = ["evol-eval"] + sys.argv[2:]; _run(SCRIPTS["eval"])
def flow():        sys.argv = ["evol-flow"] + sys.argv[2:]; _run(SCRIPTS["flow"])
def provider():    sys.argv = ["evol-provider"] + sys.argv[2:]; _run(SCRIPTS["provider"])
def shield():      sys.argv = ["evol-shield"] + sys.argv[2:]; _run(SCRIPTS["shield"])
def orchestrate(): sys.argv = ["evol-orchestrate"] + sys.argv[2:]; _run(SCRIPTS["orchestrate"])
def agent():       sys.argv = ["evol-agent"] + sys.argv[2:]; _run(SCRIPTS["agent"])
def evolve():      sys.argv = ["evol-evolve"] + sys.argv[2:]; _run(SCRIPTS["evolve"])
def research():    sys.argv = ["evol-research"] + sys.argv[2:]; _run(SCRIPTS["research"])
def memory():      sys.argv = ["evol-memory"] + sys.argv[2:]; _run(SCRIPTS["memory"])
def lessons():     sys.argv = ["evol-lessons"] + sys.argv[2:]; _run(SCRIPTS["lessons"])


def install_global() -> int:
    """Instala /evol como trigger global en los 7 IDEs soportados.

    Copia workflows a los directorios globales de cada IDE. El trigger
    queda disponible en CUALQUIER directorio del PC sin configuracion
    por proyecto — igual que /anmax funciona globalmente.

    IDEs cubiertos:
      Claude Code   ~/.claude/commands/
      OpenCode      ~/.config/opencode/command/
      Cursor        ~/.cursor/rules/<trigger>.mdc
      Windsurf      ~/.codeium/workflows/
      VSCode Copilot ~/.config/Code/User/prompts/
      Antigravity   ~/.gemini/skills/
      Codex         ~/.codex/skills/<trigger>-orchestrator/

    Uso: evol-install-global
         evol install-global
    """
    import shutil
    import subprocess

    data = _data_dir()
    scripts = _scripts_dir()
    workflows_dir = data / ".agent" / "workflows"
    skills_dir = data / "skills"
    home = Path.home()
    trigger = os.environ.get("EVOL_TRIGGER", "evol")

    if not workflows_dir.is_dir():
        print(f"[evol] workflows no encontrados en {workflows_dir}", file=sys.stderr)
        return 1

    workflows = sorted(workflows_dir.glob("*.md"))

    def copy_workflows(dest: Path, ext: str = "md") -> int:
        dest.mkdir(parents=True, exist_ok=True)
        n = 0
        for wf in workflows:
            shutil.copy2(wf, dest / f"{wf.stem}.{ext}")
            n += 1
        return n

    # 1. Claude Code
    n = copy_workflows(home / ".claude" / "commands")
    print(f"[evol] Claude Code:    {n} commands → ~/.claude/commands/")

    # 2. OpenCode
    n = copy_workflows(home / ".config" / "opencode" / "command")
    print(f"[evol] OpenCode:       {n} commands → ~/.config/opencode/command/")

    # 3. Cursor — 1 archivo .mdc orquestador (Cursor no soporta N slash commands sin MCP)
    cursor_dir = home / ".cursor" / "rules"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    mdc_content = f"""---
description: Orquestador Evol-DD. Pipeline 6 fases. Activar con @{trigger}.
globs:
alwaysApply: false
---
# /{trigger} — Orquestador Evol-DD

Activar con @{trigger}. Workflows en `.agent/workflows/`.
Lee `memoria.md` + `lecciones.md` + `CLAUDE.md` al iniciar (Constitucion Art. 3).
"""
    (cursor_dir / f"{trigger}.mdc").write_text(mdc_content, encoding="utf-8")
    print(f"[evol] Cursor:         1 rule → ~/.cursor/rules/{trigger}.mdc")

    # 4. Windsurf — workflows globales en ~/.codeium/workflows/
    n = copy_workflows(home / ".codeium" / "workflows")
    print(f"[evol] Windsurf:       {n} workflows → ~/.codeium/workflows/")

    # 5. VSCode Copilot — prompts globales
    n = copy_workflows(home / ".config" / "Code" / "User" / "prompts", ext="prompt.md")
    print(f"[evol] VSCode Copilot: {n} prompts → ~/.config/Code/User/prompts/")

    # 6. Antigravity — skills globales en ~/.gemini/skills/
    gemini_skills = home / ".gemini" / "skills"
    gemini_skills.mkdir(parents=True, exist_ok=True)
    if skills_dir.is_dir():
        n = 0
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                dst = gemini_skills / skill_dir.name
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(skill_dir, dst)
                n += 1
        print(f"[evol] Antigravity:    {n} skills → ~/.gemini/skills/")
    else:
        print(f"[evol] Antigravity:    skills/ no encontrado — skip")

    # 7. Codex — orchestrator global en ~/.codex/skills/
    adapt = scripts / "evol-adapt.sh"
    if adapt.exists():
        env = os.environ.copy()
        env["EVOL_DATA_DIR"] = str(data)
        subprocess.run(["bash", str(adapt), "codex"], env=env,
                       capture_output=True)
        print(f"[evol] Codex:          orchestrator → ~/.codex/skills/{trigger}-orchestrator/")
    else:
        print(f"[evol] Codex:          evol-adapt.sh no encontrado — skip")

    print(f"\n[evol] /{trigger} instalado globalmente en 7 IDEs.")
    print("[evol] Abrir cualquier carpeta — /evol disponible sin configuracion adicional.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
