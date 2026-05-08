"""
tabular_diagnostic.py
---------------------
Core mínimo de diagnóstico tabular para el Laboratorio de Análisis PyME.

Responsabilidad única: leer un CSV con Polars y devolver un dict con
métricas básicas de calidad de datos.  Sin red, sin Supabase, sin API.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union


def diagnosticar_csv(path: Union[str, Path], cliente_id: str) -> dict:
    """Lee un CSV y devuelve un diagnóstico básico de calidad de datos.

    Parameters
    ----------
    path:
        Ruta al archivo CSV.
    cliente_id:
        Identificador del cliente; se incluye en el resultado sin modificación.

    Returns
    -------
    dict con las claves:
        cliente_id, rows, columns, column_names,
        empty_columns, null_counts_by_column,
        duplicate_rows_count, status

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.
    ValueError
        Si la extensión no es .csv o si el archivo no puede ser leído como CSV.
    """
    import polars as pl

    path = Path(path)

    # ── Fail-closed: existencia ──────────────────────────────────────────────
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path.name}")

    # ── Fail-closed: extensión ───────────────────────────────────────────────
    if path.suffix.lower() != ".csv":
        raise ValueError(
            f"Extensión no soportada: '{path.suffix}'. Solo se aceptan archivos .csv"
        )

    # ── Lectura ──────────────────────────────────────────────────────────────
    try:
        df = pl.read_csv(path, infer_schema_length=0)  # todo como Utf8 → seguro
    except Exception as exc:
        # No re-exponer contenido del archivo en el mensaje de error
        raise ValueError(f"No se pudo leer el CSV: {type(exc).__name__}") from exc

    rows, columns = df.shape
    column_names: list[str] = df.columns

    # ── Columnas vacías (todas las celdas son null o string vacío) ───────────
    empty_columns: list[str] = []
    for col in column_names:
        series = df[col]
        # Polars read_csv con infer_schema_length=0 produce Utf8/String
        all_null_or_empty = series.is_null() | (series.cast(pl.String) == "")
        if all_null_or_empty.all():
            empty_columns.append(col)

    # ── Conteo de nulos por columna ──────────────────────────────────────────
    null_counts_by_column: dict[str, int] = {
        col: int(df[col].is_null().sum()) for col in column_names
    }

    # ── Filas duplicadas ─────────────────────────────────────────────────────
    duplicate_rows_count: int = int(rows - df.unique().height)

    return {
        "cliente_id": cliente_id,
        "rows": rows,
        "columns": columns,
        "column_names": column_names,
        "empty_columns": empty_columns,
        "null_counts_by_column": null_counts_by_column,
        "duplicate_rows_count": duplicate_rows_count,
        "status": "diagnosed",
    }
