"""Tests para evol-doc-sync.py — Inc 0 (sistema JSON/MD de ahorro de tokens)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "evol_doc_sync",
    Path(__file__).parent.parent / "scripts" / "evol-doc-sync.py",
)
doc_sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(doc_sync)


# ── helpers ───────────────────────────────────────────────────────────────────

DOC_TEMPLATE = """# {titulo}

> Cubre {titulo}. NO cubre otros subdominios.

## 1. Vision general

Contenido del subdominio {titulo} para el proyecto de prueba.

## 2. Schemas

```sql
CREATE TABLE usuarios (id INT PRIMARY KEY);
CREATE TABLE proyectos (id INT PRIMARY KEY);
```

## 3. Trazabilidad

Origen: stack.md, arquitectura.md. Relacionados: db/relaciones.md.
"""


def make_doc(folder: Path, name: str, titulo: str = None):
    folder.mkdir(parents=True, exist_ok=True)
    doc = folder / f"{name}.md"
    doc.write_text(DOC_TEMPLATE.format(titulo=titulo or name))
    return doc


# ── sync_doc ──────────────────────────────────────────────────────────────────

def test_sync_doc_crea_json(tmp_path):
    doc = make_doc(tmp_path, "esquemas")
    assert doc_sync.sync_doc(doc) is True
    assert doc.with_suffix(".json").exists()


def test_sync_doc_contenido(tmp_path):
    doc = make_doc(tmp_path / "db", "esquemas", "Esquemas SQL")
    doc_sync.sync_doc(doc)
    sidecar = json.loads(doc.with_suffix(".json").read_text())
    assert sidecar["dominio"] == "db"
    assert sidecar["subdominio"] == "esquemas"
    assert sidecar["resumen"]  # no vacio
    assert "schemas" in sidecar["secciones"]


def test_sync_doc_tokens_json_menor_que_md(tmp_path):
    """En docs sustantivos el JSON es mucho mas compacto que el MD (el caso real).

    Para docs diminutos (<100 tokens) el overhead del JSON puede igualar al MD;
    el ahorro aplica al caso real de documentacion amplia (2500+ tokens).
    """
    doc = tmp_path / "esquemas.md"
    # Doc realista: contenido amplio como en doc-granular real
    body = "\n".join(f"Linea de contenido detallado numero {i} del subdominio." for i in range(120))
    doc.write_text(f"# Esquemas SQL\n\n> Cubre esquemas. NO cubre migraciones.\n\n## Schemas\n\n{body}\n")
    doc_sync.sync_doc(doc)
    sidecar = json.loads(doc.with_suffix(".json").read_text())
    assert sidecar["tokens_json"] < sidecar["tokens_md"]
    # El ahorro debe ser sustancial (>50%) en docs reales
    ahorro = 100 - (sidecar["tokens_json"] * 100 // sidecar["tokens_md"])
    assert ahorro > 50


def test_sync_doc_extrae_entidades(tmp_path):
    doc = make_doc(tmp_path, "esquemas")
    doc_sync.sync_doc(doc)
    sidecar = json.loads(doc.with_suffix(".json").read_text())
    assert "usuarios" in sidecar["entidades"]
    assert "proyectos" in sidecar["entidades"]


def test_sync_doc_skip_si_checksum_coincide(tmp_path):
    doc = make_doc(tmp_path, "esquemas")
    assert doc_sync.sync_doc(doc) is True   # primera vez escribe
    assert doc_sync.sync_doc(doc) is False  # segunda vez skip (sin cambios)


def test_sync_doc_force_reescribe(tmp_path):
    doc = make_doc(tmp_path, "esquemas")
    doc_sync.sync_doc(doc)
    assert doc_sync.sync_doc(doc, force=True) is True


def test_sync_doc_ignora_index(tmp_path):
    folder = tmp_path
    folder.mkdir(parents=True, exist_ok=True)
    idx = folder / "INDEX.md"
    idx.write_text("# INDEX\n")
    assert doc_sync.sync_doc(idx) is False


# ── sync_folder ───────────────────────────────────────────────────────────────

def test_sync_folder_crea_index_json(tmp_path):
    folder = tmp_path / "db"
    make_doc(folder, "esquemas")
    make_doc(folder, "migraciones")
    idx = doc_sync.sync_folder(folder)
    assert (folder / "INDEX.json").exists()
    assert idx["total_docs"] == 2


def test_sync_folder_index_agrega_tokens(tmp_path):
    folder = tmp_path / "db"
    make_doc(folder, "esquemas")
    make_doc(folder, "migraciones")
    idx = doc_sync.sync_folder(folder)
    # INDEX.json debe ser mucho mas compacto que la suma de los docs
    assert idx["total_tokens_json"] < idx["total_tokens_md"]


# ── sync_all ──────────────────────────────────────────────────────────────────

def test_sync_all_recursivo(tmp_path):
    make_doc(tmp_path / "db", "esquemas")
    make_doc(tmp_path / "api", "contratos")
    master = doc_sync.sync_all(tmp_path)
    assert (tmp_path / "INDEX.json").exists()
    assert master["total_dominios"] == 2
    assert master["total_docs"] == 2


# ── verify (drift detection) ──────────────────────────────────────────────────

def test_verify_sin_drift(tmp_path):
    folder = tmp_path / "db"
    make_doc(folder, "esquemas")
    doc_sync.sync_folder(folder)
    assert doc_sync.verify(folder) == []


def test_verify_detecta_md_sin_json(tmp_path):
    folder = tmp_path / "db"
    make_doc(folder, "esquemas")
    # No sync — el .json no existe
    errors = doc_sync.verify(folder)
    assert errors
    assert "DRIFT" in errors[0]


def test_verify_detecta_md_modificado(tmp_path):
    folder = tmp_path / "db"
    doc = make_doc(folder, "esquemas")
    doc_sync.sync_doc(doc)
    # Modificar el MD sin re-sync
    doc.write_text(doc.read_text() + "\n## Nueva seccion\n\nContenido nuevo.\n")
    errors = doc_sync.verify(folder)
    assert errors
    assert "cambio sin re-sync" in errors[0]
