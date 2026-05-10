"""
Router soberano de diagnóstico operacional básico.

Endpoint:
  GET /diagnostico/{tenant_id}
      BasicOperationalDiagnosticService.build_report() → 200

El repositorio es inyectable para tests via make_diagnostic_router(db_path)
o _build_diagnostic_router(repo).
Sin async externo. Sin side effects. Fail-closed.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.basic_operational_diagnostic_service import (
    BasicOperationalDiagnosticService,
)

_DEFAULT_DB_PATH = Path("data") / "curated_evidence.db"

router = APIRouter()

_default_repo: CuratedEvidenceRepositoryBackend | None = None


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
# ---------------------------------------------------------------------------


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
