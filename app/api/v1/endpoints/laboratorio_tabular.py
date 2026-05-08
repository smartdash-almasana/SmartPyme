"""
laboratorio_tabular.py
----------------------
Endpoint mínimo para diagnóstico tabular de archivos CSV.

POST /api/v1/laboratorio/tabular/diagnostico
  - multipart: cliente_id (str) + archivo (UploadFile .csv)
  - devuelve el dict de diagnosticar_csv()
  - fail-closed: 400 para cliente_id vacío, extensión inválida, CSV ilegible
  - no persiste, no toca Supabase
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.laboratorio_pyme.tabular_diagnostic import diagnosticar_csv

router = APIRouter()

# Bytes que indican contenido binario no-texto (null bytes, BOM UTF-16, etc.)
_BINARY_SIGNATURES: tuple[bytes, ...] = (
    b"\x00",       # null byte — nunca aparece en CSV texto
    b"\xff\xfe",   # BOM UTF-16 LE
    b"\xfe\xff",   # BOM UTF-16 BE
    b"\x00\x00\xfe\xff",  # BOM UTF-32
)


def _parece_binario(content: bytes) -> bool:
    """Heurística rápida: presencia de null bytes en los primeros 512 bytes."""
    sample = content[:512]
    return b"\x00" in sample


@router.post("/diagnostico")
async def diagnostico_tabular(
    cliente_id: str = Form(...),
    archivo: UploadFile = ...,
) -> dict:
    """Recibe un CSV multipart y devuelve diagnóstico básico de calidad de datos."""

    # ── Validar cliente_id ───────────────────────────────────────────────────
    if not cliente_id or not cliente_id.strip():
        raise HTTPException(status_code=400, detail="cliente_id no puede estar vacío.")

    # ── Validar extensión antes de escribir en disco ─────────────────────────
    filename = archivo.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Solo se aceptan archivos .csv.",
        )

    # ── Leer contenido ───────────────────────────────────────────────────────
    content = await archivo.read()

    # ── Rechazar contenido binario (no es un CSV de texto) ───────────────────
    if _parece_binario(content):
        raise HTTPException(
            status_code=400,
            detail="El archivo no parece ser un CSV de texto válido.",
        )

    # ── Escribir en temp file seguro y diagnosticar ──────────────────────────
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".csv", delete=False, mode="wb"
        ) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        result = diagnosticar_csv(tmp_path, cliente_id.strip())
        return result

    except (FileNotFoundError, ValueError) as exc:
        # diagnosticar_csv ya produce mensajes limpios sin contenido sensible
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="No se pudo procesar el archivo CSV.",
        )
    finally:
        # ── Borrar temp file siempre ─────────────────────────────────────────
        if tmp_path is not None and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass  # best-effort; no bloquear la respuesta
