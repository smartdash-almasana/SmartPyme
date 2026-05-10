"""
Webhook soberano para recibir y consultar evidencia curada desde BEM.

Endpoints:
  POST /webhooks/bem
      body → BemCuratedEvidenceAdapter → CuratedEvidenceRecord → repository.create()

  GET /webhooks/bem/{tenant_id}
      repository.list_by_tenant() → 200 lista ordenada por received_at asc

  GET /webhooks/bem/{tenant_id}/{evidence_id}
      repository.get_by_evidence_id() → 200 | 404

ORDEN DE REGISTRO: el endpoint de lista ({tenant_id}) debe registrarse ANTES que el
de detalle ({tenant_id}/{evidence_id}) para que FastAPI resuelva correctamente.

El repositorio es inyectable para tests via _build_router(repo) o make_router(db_path).
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

    # ------------------------------------------------------------------
    # POST /webhooks/bem
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # GET /webhooks/bem/{tenant_id}  — lista por tenant
    # Registrado ANTES que el endpoint de detalle para evitar ambigüedad.
    # ------------------------------------------------------------------

    @local_router.get("/webhooks/bem/{tenant_id}")
    def list_evidence(tenant_id: str) -> dict[str, Any]:
        if not tenant_id.strip():
            raise HTTPException(status_code=400, detail="tenant_id es obligatorio")

        records = repo.list_by_tenant(tenant_id=tenant_id)

        return {
            "tenant_id": tenant_id,
            "items": [
                {
                    "evidence_id": r.evidence_id,
                    "kind": r.kind.value,
                    "trace_id": r.trace_id,
                    "received_at": r.received_at,
                }
                for r in records
            ],
        }

    # ------------------------------------------------------------------
    # GET /webhooks/bem/{tenant_id}/{evidence_id}  — detalle
    # ------------------------------------------------------------------

    @local_router.get("/webhooks/bem/{tenant_id}/{evidence_id}")
    def get_evidence(tenant_id: str, evidence_id: str) -> dict[str, Any]:
        if not tenant_id.strip():
            raise HTTPException(status_code=400, detail="tenant_id es obligatorio")
        if not evidence_id.strip():
            raise HTTPException(status_code=400, detail="evidence_id es obligatorio")

        record = repo.get_by_evidence_id(tenant_id=tenant_id, evidence_id=evidence_id)
        if record is None:
            raise HTTPException(status_code=404, detail="evidencia no encontrada")

        return {
            "tenant_id": record.tenant_id,
            "evidence_id": record.evidence_id,
            "kind": record.kind.value,
            "payload": record.payload,
            "trace_id": record.trace_id,
            "received_at": record.received_at,
        }

    return local_router


# ---------------------------------------------------------------------------
# Router por defecto (usa lazy singleton con _DEFAULT_DB_PATH).
# Mismo orden de registro que _build_router.
# ---------------------------------------------------------------------------


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


@router.get("/webhooks/bem/{tenant_id}")
def list_evidence(tenant_id: str) -> dict[str, Any]:
    if not tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id es obligatorio")

    records = _get_default_repo().list_by_tenant(tenant_id=tenant_id)

    return {
        "tenant_id": tenant_id,
        "items": [
            {
                "evidence_id": r.evidence_id,
                "kind": r.kind.value,
                "trace_id": r.trace_id,
                "received_at": r.received_at,
            }
            for r in records
        ],
    }


@router.get("/webhooks/bem/{tenant_id}/{evidence_id}")
def get_evidence(tenant_id: str, evidence_id: str) -> dict[str, Any]:
    if not tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id es obligatorio")
    if not evidence_id.strip():
        raise HTTPException(status_code=400, detail="evidence_id es obligatorio")

    record = _get_default_repo().get_by_evidence_id(
        tenant_id=tenant_id, evidence_id=evidence_id
    )
    if record is None:
        raise HTTPException(status_code=404, detail="evidencia no encontrada")

    return {
        "tenant_id": record.tenant_id,
        "evidence_id": record.evidence_id,
        "kind": record.kind.value,
        "payload": record.payload,
        "trace_id": record.trace_id,
        "received_at": record.received_at,
    }
