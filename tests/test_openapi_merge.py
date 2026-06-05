"""Tests para evol-openapi-merge.py — Inc 6 (openapi fragments + raiz generada)."""
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "evol_openapi_merge",
    Path(__file__).parent.parent / "scripts" / "evol-openapi-merge.py",
)
merge_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(merge_mod)


def _fragments(tmp_path):
    frag = tmp_path / "fragments"
    frag.mkdir()
    (frag / "_root.yaml").write_text(
        "openapi: 3.0.3\ninfo:\n  title: Test\n  version: 1.0.0\npaths: {}\ncomponents:\n  schemas: {}\n"
    )
    (frag / "users.yaml").write_text(
        "paths:\n  /users:\n    get:\n      responses:\n        '200':\n          description: OK\n"
        "components:\n  schemas:\n    User:\n      type: object\n"
    )
    (frag / "orders.yaml").write_text(
        "paths:\n  /orders:\n    get:\n      responses:\n        '200':\n          description: OK\n"
    )
    return frag


def test_merge_combina_paths(tmp_path):
    frag = _fragments(tmp_path)
    out = tmp_path / "openapi.yaml"
    root = merge_mod.merge_fragments(frag, out)
    assert "/users" in root["paths"]
    assert "/orders" in root["paths"]


def test_merge_combina_schemas(tmp_path):
    frag = _fragments(tmp_path)
    out = tmp_path / "openapi.yaml"
    root = merge_mod.merge_fragments(frag, out)
    assert "User" in root["components"]["schemas"]


def test_merge_genera_banner(tmp_path):
    frag = _fragments(tmp_path)
    out = tmp_path / "openapi.yaml"
    merge_mod.merge_fragments(frag, out)
    assert "GENERADO automaticamente" in out.read_text()


def test_merge_ignora_root_yaml_como_fragmento(tmp_path):
    frag = _fragments(tmp_path)
    out = tmp_path / "openapi.yaml"
    root = merge_mod.merge_fragments(frag, out)
    # _root.yaml aporta metadata, no es un fragmento de paths
    assert root["info"]["title"] == "Test"


def test_validate_root_valido(tmp_path):
    frag = _fragments(tmp_path)
    out = tmp_path / "openapi.yaml"
    merge_mod.merge_fragments(frag, out)
    assert merge_mod.validate_root(out) == []


def test_validate_root_sin_openapi_falla(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("info:\n  title: x\npaths: {}\n")
    errors = merge_mod.validate_root(bad)
    assert any("openapi" in e.lower() for e in errors)


def test_validate_root_inexistente(tmp_path):
    errors = merge_mod.validate_root(tmp_path / "noexiste.yaml")
    assert errors
