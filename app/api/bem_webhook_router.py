"""
Webhook soberano para recibir evidencia curada desde BEM.

Pipeline: body → BemCuratedEvidenceAdapter → CuratedEvidenceRecord → repository.create()

El repositorio es inyectable para tests; el default usa data/curated_evidence.db.
Sin async externo. Sin side effects. Fail-closed.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.bem_curated_evidence_adapter import BemCuratedEvidenceAdapter

_DEFAULT_DB_PATH = Path("data") / "curated_evidence.db"

router = APIRouter()

# Repositorio singleton por defecto (lazy-init en primera petición real).
# Los tests inyectan su propio repositorio via override de dependencia o
# usando _make_router() directamente.
_default_repo: CuratedEvidenceRepositoryBackend | None = None


def _get_default_repo() -> CuratedEvidenceRepositoryBackend:
    global _default_repo
    if _default_repo is None:
        _DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _default_repo = CuratedEvidenceRepositoryBackend(db_path=_DEFAULT_DB_PATH)
    return _default_repo


def make_router(
    db_path: str | Path | None = None,
) -> APIRouter:
    """
    Construye un APIRouter con repositorio propio.

    Útil para tests y para montar el router con un path de DB configurable.
    Si db_path es None usa _DEFAULT_DB_PATH.
    """
    resolved_path = Path(db_path) if db_path is not None else _DEFAULT_DB_PATH
    repo = CuratedEvidenceRepositoryBackend(db_path=resolved_path)
    return _build_router(repo)


def _build_router(repo: CuratedEvidenceRepositoryBackend) -> APIRouter:
    local_router = APIRouter()

    @local_router.post("/webhooks/bem")
    def bem_webhook(body: dict[str, Any]) -> dict[str, str]:
        tenant_id = body.get("tenant_id")
        payload = body.get("payload")

        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise HTTPException(status_code=400, detail="tenant_id es obligatorio")
        if not isinstance(payload, dict) or not payload:
            raise HTTPException(status_code=400, detail="payload es obligatorio")

        try:
            record = BemCuratedEvidenceAdapter().build_curated_evidence(
                tenant_id=tenant_id,
                payload=payload,
            )
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        try:
            repo.create(record)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return {
            "status": "accepted",
            "tenant_id": record.tenant_id,
            "evidence_id": record.evidence_id,
        }

    return local_router


# Router por defecto montado en el módulo (usa lazy singleton).
# Para producción se puede reemplazar con make_router(db_path=...).
@router.post("/webhooks/bem")
def bem_webhook(body: dict[str, Any]) -> dict[str, str]:
    tenant_id = body.get("tenant_id")
    payload = body.get("payload")

    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id es obligatorio")
    if not isinstance(payload, dict) or not payload:
        raise HTTPException(status_code=400, detail="payload es obligatorio")

    try:
        record = BemCuratedEvidenceAdapter().build_curated_evidence(
            tenant_id=tenant_id,
            payload=payload,
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        _get_default_repo().create(record)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "status": "accepted",
        "tenant_id": record.tenant_id,
        "evidence_id": record.evidence_id,
    }
