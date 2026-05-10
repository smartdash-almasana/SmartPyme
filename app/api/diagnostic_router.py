"""
Router soberano de diagnóstico operacional básico.

Endpoints:
  GET /diagnostico/{tenant_id}/informe
      → text/markdown con informe exportable

  GET /diagnostico/{tenant_id}
      → JSON con findings y evidence_count

ORDEN DE REGISTRO: /informe debe registrarse ANTES que /{tenant_id} para que
FastAPI no interprete "informe" como un tenant_id.

El repositorio es inyectable para tests via make_diagnostic_router(db_path)
o _build_diagnostic_router(repo).
Sin async externo. Sin side effects. Fail-closed.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.basic_operational_diagnostic_service import (
    BasicOperationalDiagnosticService,
)
from app.services.markdown_diagnostic_report_builder import MarkdownDiagnosticReportBuilder

_DEFAULT_DB_PATH = Path("data") / "curated_evidence.db"


def _safe_filename_tenant(tenant_id: str) -> str:
    """
    Sanitiza tenant_id para uso seguro en Content-Disposition filename.

    - Reemplaza cualquier carácter no alfanumérico, guion o underscore por "_".
    - Colapsa múltiples "_" consecutivos a uno.
    - Si el resultado queda vacío, retorna "tenant".
    """
    safe = re.sub(r"[^a-zA-Z0-9\-_]", "_", tenant_id)
    safe = re.sub(r"_+", "_", safe)
    safe = safe.strip("_")
    return safe if safe else "tenant"

router = APIRouter()

_default_repo: CuratedEvidenceRepositoryBackend | None = None

_md_builder = MarkdownDiagnosticReportBuilder()


def _get_default_repo() -> CuratedEvidenceRepositoryBackend:
    global _default_repo
    if _default_repo is None:
        _DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _default_repo = CuratedEvidenceRepositoryBackend(db_path=_DEFAULT_DB_PATH)
    return _default_repo


def make_diagnostic_router(
    db_path: str | Path | None = None,
) -> APIRouter:
    """
    Construye un APIRouter con repositorio propio.

    Útil para tests y para montar el router con un path de DB configurable.
    Si db_path es None usa _DEFAULT_DB_PATH.
    """
    resolved_path = Path(db_path) if db_path is not None else _DEFAULT_DB_PATH
    repo = CuratedEvidenceRepositoryBackend(db_path=resolved_path)
    return _build_diagnostic_router(repo)


def _build_diagnostic_router(repo: CuratedEvidenceRepositoryBackend) -> APIRouter:
    local_router = APIRouter()
    service = BasicOperationalDiagnosticService(repository=repo)
    builder = MarkdownDiagnosticReportBuilder()

    # ------------------------------------------------------------------
    # GET /diagnostico/{tenant_id}/informe
    # Registrado ANTES que /{tenant_id} para evitar ambigüedad de path.
    # ------------------------------------------------------------------

    @local_router.get("/diagnostico/{tenant_id}/informe")
    def get_informe(tenant_id: str) -> Response:
        if not tenant_id.strip():
            raise HTTPException(status_code=400, detail="tenant_id es obligatorio")

        try:
            report = service.build_report(tenant_id=tenant_id)
            markdown = builder.build_markdown_report(report)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return Response(
            content=markdown,
            media_type="text/markdown",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="diagnostico-{_safe_filename_tenant(tenant_id)}.md"'
                )
            },
        )

    # ------------------------------------------------------------------
    # GET /diagnostico/{tenant_id}
    # ------------------------------------------------------------------

    @local_router.get("/diagnostico/{tenant_id}")
    def get_diagnostico(tenant_id: str) -> dict[str, Any]:
        if not tenant_id.strip():
            raise HTTPException(status_code=400, detail="tenant_id es obligatorio")

        try:
            report = service.build_report(tenant_id=tenant_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return report

    return local_router


# ---------------------------------------------------------------------------
# Router por defecto (usa lazy singleton con _DEFAULT_DB_PATH).
# Mismo orden de registro que _build_diagnostic_router.
# ---------------------------------------------------------------------------


@router.get("/diagnostico/{tenant_id}/informe")
def get_informe(tenant_id: str) -> Response:
    if not tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id es obligatorio")

    service = BasicOperationalDiagnosticService(repository=_get_default_repo())

    try:
        report = service.build_report(tenant_id=tenant_id)
        markdown = _md_builder.build_markdown_report(report)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={
            "Content-Disposition": (
                f'attachment; filename="diagnostico-{_safe_filename_tenant(tenant_id)}.md"'
            )
        },
    )


@router.get("/diagnostico/{tenant_id}")
def get_diagnostico(tenant_id: str) -> dict[str, Any]:
    if not tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id es obligatorio")

    service = BasicOperationalDiagnosticService(repository=_get_default_repo())

    try:
        report = service.build_report(tenant_id=tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return report
