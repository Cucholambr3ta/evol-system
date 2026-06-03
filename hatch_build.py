"""Hatchling build hook — ejecuta evol-install-global post pip install.

Hatchling llama a initialize() durante la construccion del wheel y a
finalize() despues de que pip instala el paquete en el entorno destino.

El hook post-install copia /evol a los dirs globales de los 7 IDEs:
  ~/.claude/commands/           Claude Code
  ~/.config/opencode/command/   OpenCode
  ~/.cursor/rules/              Cursor
  ~/.codeium/workflows/         Windsurf
  ~/.config/Code/User/prompts/  VSCode Copilot
  ~/.gemini/skills/             Antigravity
  ~/.codex/skills/              Codex
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Hook que instala los triggers IDE globalmente post pip install."""

    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict) -> None:
        # No hace nada durante la construccion del wheel
        pass

    def finalize(self, version: str, build_data: dict, artifact_path: str) -> None:
        """Se ejecuta despues de que pip instala el paquete."""
        _run_install_global()


def _run_install_global() -> None:
    """Llama a install_global() del paquete instalado."""
    try:
        # Importar desde el paquete recien instalado
        from evol_cli import install_global
        print("\n[evol] Configurando triggers globales en IDEs...")
        result = install_global()
        if result == 0:
            print("[evol] Instalacion completa. /evol disponible en todos los IDEs.")
        else:
            print("[evol] WARN: algunos IDEs pueden no haberse configurado.", file=sys.stderr)
    except Exception as e:
        # Nunca fallar el install por esto — solo advertir
        print(f"[evol] WARN: no se pudieron instalar triggers globales: {e}", file=sys.stderr)
        print("[evol] Correr manualmente: evol-install-global", file=sys.stderr)
