"""Tests para evol-security-inventory.py — INC-3 (arsenal seguridad por componente)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "evol_security_inventory",
    Path(__file__).parent.parent / "scripts" / "evol-security-inventory.py",
)
inv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inv)


# ── tools_for_components ──────────────────────────────────────────────────────

def test_siempre_incluye_scan_shield():
    tools = inv.tools_for_components([])
    assert "evol-scan" in tools
    assert "evol-shield" in tools


def test_auth_incluye_pentest_stride():
    tools = inv.tools_for_components(["auth"])
    assert "stride" in tools
    assert "nuclei" in tools


def test_api_incluye_dast_zap():
    tools = inv.tools_for_components(["api"])
    assert "zap" in tools
    assert "nuclei" in tools


def test_parser_incluye_fuzz_crash():
    tools = inv.tools_for_components(["parser"])
    assert "pruebas-fuzz" in tools
    assert "evol-crash" in tools


def test_db_incluye_trivy():
    tools = inv.tools_for_components(["db"])
    assert "trivy" in tools


def test_componente_desconocido_solo_siempre():
    tools = inv.tools_for_components(["inexistente"])
    assert tools == inv.ALWAYS


def test_multiples_componentes_sin_duplicados():
    tools = inv.tools_for_components(["auth", "api", "db"])
    assert len(tools) == len(set(tools))


# ── gen_checklist ─────────────────────────────────────────────────────────────

def test_checklist_externa_instalada(monkeypatch):
    ext = {"semgrep": True, "gitleaks": True, "trivy": True, "nuclei": True, "zap": True}
    out = inv.gen_checklist(["api"], ext)
    assert "nuclei" in out
    assert "SKIP nuclei" not in out


def test_checklist_externa_faltante_marca_skip():
    ext = {"semgrep": False, "gitleaks": False, "trivy": False, "nuclei": False, "zap": False}
    out = inv.gen_checklist(["api"], ext)
    assert "SKIP zap" in out
    assert "Instalar:" in out


def test_checklist_auth_incluye_pentest_agentico():
    ext = {t: True for t in inv.EXTERNAL_TOOLS}
    out = inv.gen_checklist(["auth"], ext)
    assert "advanced-agentic-pentesting" in out
    assert "Verificar exploit" in out


def test_checklist_componente_no_critico_sin_pentest_agentico():
    ext = {t: True for t in inv.EXTERNAL_TOOLS}
    out = inv.gen_checklist(["deps"], ext)
    assert "advanced-agentic-pentesting" not in out


def test_checklist_nativas_siempre_presentes():
    out = inv.gen_checklist([], {t: False for t in inv.EXTERNAL_TOOLS})
    assert "evol-scan" in out
    assert "evol-shield" in out


# ── gen_readme_section ────────────────────────────────────────────────────────

def test_readme_lista_nativas_y_externas():
    ext = {"semgrep": True, "gitleaks": False, "trivy": True, "nuclei": True, "zap": False}
    section = inv.gen_readme_section(ext)
    assert "Herramientas de Seguridad" in section
    assert "evol-scan" in section  # nativa
    assert "semgrep" in section   # externa
    assert "instalado" in section
    assert "FALTANTE" in section


def test_readme_incluye_mapeo_componentes():
    section = inv.gen_readme_section({t: False for t in inv.EXTERNAL_TOOLS})
    assert "Mapeo componente" in section
    assert "auth" in section


# ── CLI ───────────────────────────────────────────────────────────────────────

def test_cli_checklist_json(capsys):
    inv.main(["checklist", "--components=auth", "--format=json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "auth" in data["components"]
    assert "evol-scan" in data["tools"]


def test_cli_readme_write(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Proyecto\n\nDescripcion.\n")
    inv.main(["readme", "--write", str(readme)])
    content = readme.read_text()
    assert "## Herramientas de Seguridad" in content


def test_cli_readme_reemplaza_seccion_existente(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# P\n\n## Herramientas de Seguridad\n\nvieja.\n\n## Otra\n\nx.\n")
    inv.main(["readme", "--write", str(readme)])
    content = readme.read_text()
    assert content.count("## Herramientas de Seguridad") == 1
    assert "## Otra" in content  # preserva otras secciones
