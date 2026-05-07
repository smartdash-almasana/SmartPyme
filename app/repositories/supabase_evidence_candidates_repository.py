"""Adapter Supabase para evidence_candidates — SmartPyme P0.

Implementa EvidenceCandidatePort usando un cliente Supabase inyectable.
El cliente real es `supabase.Client` (librería supabase-py).
En tests se inyecta un FakeSupabaseClient sin red.

Puente de contrato (CONTRACT_BRIDGE):
    El schema draft define `evidence_candidates` con columnas:
        evidence_id, job_id, case_id, evidence_type, payload, result,
        metadata, score, status.

    El contrato de dominio más cercano es `EvidenceChunk` (evidence_contract.py):
        evidence_id     → evidence_id
        job_id          → job_id
        cliente_id      → cliente_id
        text            → payload["text"]
        filename        → payload["filename"]
        page            → payload["page"]
        chunk_order     → payload["chunk_order"]
        document_id     → payload["document_id"]
        raw_document_id → payload["raw_document_id"]
        plan_id         → metadata["plan_id"]
        metadata        → metadata (merged)
        case_id         → None (EvidenceChunk no tiene case_id; reservado)
        evidence_type   → "chunk" (fijo para EvidenceChunk)
        score           → None (EvidenceChunk no tiene score; reservado)
        status          → "candidate" (default del schema)
        result          → None (reservado para post-procesamiento)

    Si en el futuro se persiste ExtractedFactCandidate, el adapter puede
    extenderse con un segundo método create_fact_candidate() sin romper
    el contrato actual.

Reglas:
    - cliente_id es OBLIGATORIO. Fail-closed si está vacío.
    - Todas las operaciones filtran por cliente_id.
    - create() rechaza mismatch entre candidate.cliente_id y self.cliente_id.
    - list_by_job() filtra por cliente_id y job_id.
    - Si no se inyecta cliente explícito, se valida el entorno Supabase.
    - No modifica repositorios SQLite legacy.
    - No hace dual-write.
    - payload y metadata se insertan como dict (JSON-compatible), nunca stringified.

Tabla Supabase esperada: evidence_candidates
    cliente_id      TEXT NOT NULL
    evidence_id     TEXT NOT NULL
    job_id          TEXT
    case_id         TEXT
    evidence_type   TEXT
    payload         JSONB
    result          JSONB
    metadata        JSONB
    score           NUMERIC(6,5)
    status          TEXT NOT NULL DEFAULT 'candidate'
    created_at      TIMESTAMPTZ
    updated_at      TIMESTAMPTZ
    PRIMARY KEY (cliente_id, evidence_id)
"""
from __future__ import annotations

from typing import Any

from app.contracts.evidence_contract import EvidenceChunk
from app.repositories.persistence_provider import validate_supabase_env

_TABLE = "evidence_candidates"
_EVIDENCE_TYPE_CHUNK = "chunk"
_STATUS_CANDIDATE = "candidate"


class SupabaseEvidenceCandidatesRepository:
    """Adapter Supabase para evidence_candidates. Implementa EvidenceCandidatePort.

    Persiste EvidenceChunk como entidad primaria. Ver CONTRACT_BRIDGE en el
    módulo docstring para el mapeo completo de campos.

    Args:
        cliente_id: Identificador del tenant. Obligatorio. Fail-closed si vacío.
        supabase_client: Cliente Supabase inyectable. Si es None, se valida
            el entorno (SMARTPYME_SUPABASE_URL / SMARTPYME_SUPABASE_KEY) y se
            construye el cliente real. En tests, inyectar un FakeSupabaseClient.
    """

    def __init__(
        self,
        cliente_id: str,
        supabase_client: Any | None = None,
    ) -> None:
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required")

        self.cliente_id = cliente_id

        if supabase_client is None:
            # Sin cliente inyectado → validar entorno y construir cliente real.
            validate_supabase_env()
            self._client = self._build_real_client()
        else:
            self._client = supabase_client

    # ------------------------------------------------------------------
    # EvidenceCandidatePort interface
    # ------------------------------------------------------------------

    def create(self, candidate: EvidenceChunk) -> None:
        """Persiste un nuevo candidato de evidencia en Supabase.

        Fail-closed si candidate.cliente_id difiere de self.cliente_id.

        Args:
            candidate: Instancia de EvidenceChunk. candidate.cliente_id debe
                       coincidir con el cliente_id del adapter.

        Raises:
            ValueError: Si candidate.cliente_id difiere de self.cliente_id (mismatch).
        """
        if candidate.cliente_id != self.cliente_id:
            raise ValueError(
                f"cliente_id mismatch: repo={self.cliente_id!r}, "
                f"candidate={candidate.cliente_id!r}"
            )

        # payload: campos de contenido del chunk.
        payload: dict[str, Any] = {
            "text": candidate.text,
            "filename": candidate.filename,
            "page": candidate.page,
            "chunk_order": candidate.chunk_order,
            "document_id": candidate.document_id,
        }
        if candidate.raw_document_id:
            payload["raw_document_id"] = candidate.raw_document_id

        # metadata: campos auxiliares + metadata del contrato.
        metadata: dict[str, Any] = dict(candidate.metadata)
        if candidate.plan_id:
            metadata["plan_id"] = candidate.plan_id

        row: dict[str, Any] = {
            "cliente_id": self.cliente_id,
            "evidence_id": candidate.evidence_id,
            "job_id": candidate.job_id if candidate.job_id else None,
            "case_id": None,  # EvidenceChunk no tiene case_id; reservado.
            "evidence_type": _EVIDENCE_TYPE_CHUNK,
            "payload": payload,
            "result": None,
            "metadata": metadata,
            "score": None,  # EvidenceChunk no tiene score; reservado.
            "status": _STATUS_CANDIDATE,
        }

        (
            self._client
            .table(_TABLE)
            .insert(row)
            .execute()
        )

    def get(self, evidence_id: str) -> EvidenceChunk | None:
        """Recupera un candidato por evidence_id, filtrado por cliente_id.

        Returns:
            Instancia de EvidenceChunk o None si no existe para este cliente.
        """
        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("cliente_id", self.cliente_id)
            .eq("evidence_id", evidence_id)
            .execute()
        )

        rows = response.data
        if not rows:
            return None

        return self._row_to_chunk(rows[0])

    def list_by_job(self, job_id: str) -> list[EvidenceChunk]:
        """Lista candidatos de evidencia para un job específico del cliente.

        Filtra por cliente_id y job_id. Nunca retorna evidencia de otros clientes.

        Args:
            job_id: Identificador del job.

        Returns:
            Lista de EvidenceChunk para este cliente y job.
        """
        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("cliente_id", self.cliente_id)
            .eq("job_id", job_id)
            .execute()
        )

        return [self._row_to_chunk(row) for row in response.data]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_chunk(row: dict[str, Any]) -> EvidenceChunk:
        """Convierte una fila de Supabase a instancia de EvidenceChunk.

        Reconstruye los campos de contenido desde payload y los auxiliares
        desde metadata.
        """
        payload = row.get("payload") or {}
        metadata = row.get("metadata") or {}

        # Extraer plan_id de metadata si fue almacenado allí.
        plan_id = metadata.pop("plan_id", None)

        return EvidenceChunk(
            cliente_id=row["cliente_id"],
            evidence_id=row["evidence_id"],
            document_id=payload.get("document_id", ""),
            raw_document_id=payload.get("raw_document_id"),
            job_id=row.get("job_id"),
            plan_id=plan_id,
            filename=payload.get("filename", ""),
            page=payload.get("page", 0),
            text=payload.get("text", ""),
            chunk_order=payload.get("chunk_order", 0),
            metadata=dict(metadata),
        )

    @staticmethod
    def _build_real_client() -> Any:
        """Construye el cliente Supabase real usando variables de entorno.

        Solo se llama cuando no se inyecta un cliente explícito y el entorno
        ya fue validado por validate_supabase_env().

        Raises:
            ImportError: Si la librería supabase-py no está instalada.
        """
        import os

        try:
            from supabase import create_client  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "BLOCKED_MISSING_DEPENDENCY: la librería 'supabase' no está instalada. "
                "Instalar con: pip install supabase"
            ) from exc

        url = os.environ["SMARTPYME_SUPABASE_URL"]
        key = os.environ["SMARTPYME_SUPABASE_KEY"]
        return create_client(url, key)
