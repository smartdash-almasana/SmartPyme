"""
test_tabular_diagnostic.py
--------------------------
Tests sin red para diagnosticar_csv().
Todos los archivos CSV se crean en tmp_path (pytest fixture).
"""
from __future__ import annotations

import pytest

from app.laboratorio_pyme.tabular_diagnostic import diagnosticar_csv


# ── helpers ─────────────────────────────────────────────────────────────────

def _write_csv(tmp_path, name: str, content: str):
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ── tests ────────────────────────────────────────────────────────────────────

def test_csv_valido_basico(tmp_path):
    """CSV limpio: rows, columns y status correctos."""
    csv = _write_csv(tmp_path, "ventas.csv", "producto,precio,cantidad\nA,100,5\nB,200,3\n")
    result = diagnosticar_csv(csv, "cliente_001")

    assert result["cliente_id"] == "cliente_001"
    assert result["rows"] == 2
    assert result["columns"] == 3
    assert result["column_names"] == ["producto", "precio", "cantidad"]
    assert result["status"] == "diagnosed"
    assert result["empty_columns"] == []
    assert result["duplicate_rows_count"] == 0


def test_csv_columna_vacia(tmp_path):
    """Columna completamente vacía aparece en empty_columns."""
    csv = _write_csv(
        tmp_path, "datos.csv",
        "nombre,vacio,valor\nJuan,,10\nPedro,,20\n"
    )
    result = diagnosticar_csv(csv, "cliente_002")

    assert "vacio" in result["empty_columns"]
    assert "nombre" not in result["empty_columns"]
    assert "valor" not in result["empty_columns"]


def test_csv_con_nulos(tmp_path):
    """null_counts_by_column refleja celdas vacías como nulos."""
    # Polars read_csv con infer_schema_length=0 trata celdas vacías como ""
    # pero celdas ausentes al final de línea pueden ser null.
    # Usamos comillas para forzar null explícito con campo vacío entre comas.
    csv = _write_csv(
        tmp_path, "nulos.csv",
        "a,b,c\n1,,3\n4,,6\n"
    )
    result = diagnosticar_csv(csv, "cliente_003")

    # columna "b" tiene 2 filas con valor vacío → empty_columns
    assert "b" in result["empty_columns"]
    assert result["status"] == "diagnosed"


def test_csv_con_duplicados(tmp_path):
    """duplicate_rows_count cuenta filas idénticas."""
    csv = _write_csv(
        tmp_path, "dup.csv",
        "x,y\n1,2\n1,2\n3,4\n"
    )
    result = diagnosticar_csv(csv, "cliente_004")

    assert result["duplicate_rows_count"] == 1
    assert result["rows"] == 3


def test_csv_sin_duplicados(tmp_path):
    """Sin duplicados → duplicate_rows_count == 0."""
    csv = _write_csv(
        tmp_path, "unico.csv",
        "x,y\n1,2\n3,4\n5,6\n"
    )
    result = diagnosticar_csv(csv, "cliente_005")

    assert result["duplicate_rows_count"] == 0


def test_archivo_inexistente(tmp_path):
    """FileNotFoundError si el archivo no existe."""
    with pytest.raises(FileNotFoundError, match="no encontrado"):
        diagnosticar_csv(tmp_path / "no_existe.csv", "cliente_006")


def test_extension_invalida(tmp_path):
    """ValueError si la extensión no es .csv."""
    xlsx = tmp_path / "datos.xlsx"
    xlsx.write_bytes(b"fake xlsx content")

    with pytest.raises(ValueError, match="Extensión no soportada"):
        diagnosticar_csv(xlsx, "cliente_007")


def test_extension_txt_invalida(tmp_path):
    """ValueError también para .txt aunque tenga contenido CSV-like."""
    txt = _write_csv(tmp_path, "datos.txt", "a,b\n1,2\n")

    with pytest.raises(ValueError, match="Extensión no soportada"):
        diagnosticar_csv(txt, "cliente_008")


def test_resultado_contiene_todas_las_claves(tmp_path):
    """El dict de resultado siempre tiene las 8 claves del contrato."""
    csv = _write_csv(tmp_path, "mini.csv", "col1,col2\nv1,v2\n")
    result = diagnosticar_csv(csv, "cliente_009")

    expected_keys = {
        "cliente_id",
        "rows",
        "columns",
        "column_names",
        "empty_columns",
        "null_counts_by_column",
        "duplicate_rows_count",
        "status",
    }
    assert expected_keys == set(result.keys())


def test_null_counts_by_column_estructura(tmp_path):
    """null_counts_by_column es un dict col→int para cada columna."""
    csv = _write_csv(tmp_path, "nc.csv", "a,b,c\n1,2,3\n4,,6\n")
    result = diagnosticar_csv(csv, "cliente_010")

    nc = result["null_counts_by_column"]
    assert isinstance(nc, dict)
    assert set(nc.keys()) == {"a", "b", "c"}
    assert all(isinstance(v, int) for v in nc.values())


def test_csv_una_sola_fila(tmp_path):
    """CSV con una sola fila de datos funciona correctamente."""
    csv = _write_csv(tmp_path, "one.csv", "x,y\n42,hello\n")
    result = diagnosticar_csv(csv, "cliente_011")

    assert result["rows"] == 1
    assert result["duplicate_rows_count"] == 0
    assert result["status"] == "diagnosed"


def test_csv_vacio_solo_header(tmp_path):
    """CSV con solo header (0 filas de datos) devuelve rows=0."""
    csv = _write_csv(tmp_path, "empty.csv", "a,b,c\n")
    result = diagnosticar_csv(csv, "cliente_012")

    assert result["rows"] == 0
    assert result["columns"] == 3
    assert result["status"] == "diagnosed"
