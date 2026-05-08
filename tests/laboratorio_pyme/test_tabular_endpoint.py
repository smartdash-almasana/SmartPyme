"""
test_tabular_endpoint.py
------------------------
Tests sin red para POST /api/v1/laboratorio/tabular/diagnostico.
"""
from __future__ import annotations

import io

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.api import api_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    return app


@pytest.fixture(scope="module")
def client():
    return TestClient(create_app())


# ── helpers ──────────────────────────────────────────────────────────────────

def _multipart(cliente_id: str, filename: str, content: bytes | str):
    if isinstance(content, str):
        content = content.encode("utf-8")
    return {
        "cliente_id": (None, cliente_id),
        "archivo": (filename, io.BytesIO(content), "text/csv"),
    }


# ── tests ─────────────────────────────────────────────────────────────────────

def test_csv_valido_devuelve_diagnostico(client):
    """CSV limpio → 200 con todas las claves del contrato."""
    files = _multipart(
        "cliente_test_01",
        "ventas.csv",
        "producto,precio,cantidad\nA,100,5\nB,200,3\n",
    )
    res = client.post("/api/v1/laboratorio/tabular/diagnostico", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["cliente_id"] == "cliente_test_01"
    assert data["rows"] == 2
    assert data["columns"] == 3
    assert data["status"] == "diagnosed"
    assert "column_names" in data
    assert "empty_columns" in data
    assert "null_counts_by_column" in data
    assert "duplicate_rows_count" in data


def test_cliente_id_vacio_400(client):
    """cliente_id vacío → 4xx (400 o 422 según validación)."""
    files = _multipart("", "datos.csv", "a,b\n1,2\n")
    res = client.post("/api/v1/laboratorio/tabular/diagnostico", files=files)
    assert res.status_code in (400, 422)


def test_cliente_id_solo_espacios_400(client):
    """cliente_id con solo espacios → 400."""
    files = _multipart("   ", "datos.csv", "a,b\n1,2\n")
    res = client.post("/api/v1/laboratorio/tabular/diagnostico", files=files)
    assert res.status_code == 400


def test_extension_invalida_xlsx_400(client):
    """Archivo .xlsx → 400 con mensaje claro."""
    files = _multipart("cliente_x", "datos.xlsx", b"fake xlsx bytes")
    res = client.post("/api/v1/laboratorio/tabular/diagnostico", files=files)
    assert res.status_code == 400
    assert "csv" in res.json()["detail"].lower()


def test_extension_invalida_txt_400(client):
    """Archivo .txt → 400."""
    files = _multipart("cliente_x", "datos.txt", "a,b\n1,2\n")
    res = client.post("/api/v1/laboratorio/tabular/diagnostico", files=files)
    assert res.status_code == 400


def test_csv_ilegible_400(client):
    """Bytes binarios con extensión .csv → 400 (CSV ilegible)."""
    files = _multipart("cliente_x", "roto.csv", b"\x00\x01\x02\x03\xff\xfe")
    res = client.post("/api/v1/laboratorio/tabular/diagnostico", files=files)
    assert res.status_code == 400


def test_endpoint_no_expone_secrets(client):
    """La respuesta de error no contiene secrets ni URLs de Supabase."""
    files = _multipart("cliente_x", "datos.xlsx", b"fake")
    res = client.post("/api/v1/laboratorio/tabular/diagnostico", files=files)
    body = res.text
    assert "supabase.co" not in body
    assert "service_role" not in body
    assert "SMARTPYME_SUPABASE" not in body


def test_csv_con_duplicados(client):
    """duplicate_rows_count correcto vía endpoint."""
    files = _multipart(
        "cliente_dup",
        "dup.csv",
        "x,y\n1,2\n1,2\n3,4\n",
    )
    res = client.post("/api/v1/laboratorio/tabular/diagnostico", files=files)
    assert res.status_code == 200
    assert res.json()["duplicate_rows_count"] == 1


def test_csv_columna_vacia(client):
    """empty_columns detectado vía endpoint."""
    files = _multipart(
        "cliente_empty",
        "empty_col.csv",
        "nombre,vacio,valor\nJuan,,10\nPedro,,20\n",
    )
    res = client.post("/api/v1/laboratorio/tabular/diagnostico", files=files)
    assert res.status_code == 200
    assert "vacio" in res.json()["empty_columns"]


def test_temp_file_no_queda_en_disco(client, tmp_path, monkeypatch):
    """El archivo temporal es eliminado después del request."""
    created: list = []
    original_nf = __import__("tempfile").NamedTemporaryFile

    import tempfile as _tf

    def _tracking_nf(**kwargs):
        f = original_nf(**kwargs)
        created.append(f.name)
        return f

    monkeypatch.setattr(_tf, "NamedTemporaryFile", _tracking_nf)

    files = _multipart("cliente_cleanup", "clean.csv", "a,b\n1,2\n")
    res = client.post("/api/v1/laboratorio/tabular/diagnostico", files=files)
    assert res.status_code == 200

    from pathlib import Path
    for p in created:
        assert not Path(p).exists(), f"Temp file no fue eliminado: {p}"
