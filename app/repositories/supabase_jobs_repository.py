"""Adapter Supabase para jobs (background_jobs) — SmartPyme P0.

Implementa JobPort usando un cliente Supabase inyectable.
El cliente real es `supabase.Client` (librería supabase-py).
En tests se inyecta un FakeSupabaseClient sin red.

Reglas:
    - cliente_id es OBLIGATORIO. Fail-closed si está vacío.
    - Todas las operaciones filtran por cliente_id.
    - create() rechaza mismatch entre job.cliente_id y self.cliente_id.
    - Si no se inyecta cliente explícito, se valida el entorno Supabase.
    - No modifica JobRepository (SQLite legacy).
    - No hace dual-write.

Tabla Supabase esperada: background_jobs
    cliente_id      TEXT NOT NULL
    job_id          TEXT NOT NULL
    job_type        TEXT NOT NULL
    status          TEXT NOT NULL
    payload         JSONB
    result          JSONB
    error_log       TEXT
    traceable_origin JSONB
    created_at      TIMESTAMPTZ
    updated_at      TIMESTAMPTZ
    PRIMARY KEY (cliente_id, job_id)
"""
from __future__ import annotations

from typing import Any

from app.contracts.job_contract import Job, JobStatus
from app.repositories.persistence_provider import validate_supabase_env

_TABLE = "background_jobs"


class SupabaseJobsRepository:
    """Adapter Supabase para jobs. Implementa JobPort.

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
    # JobPort interface
    # ------------------------------------------------------------------

    def create(self, job: Job) -> None:
        """Persiste un nuevo job en Supabase.

        Fail-closed si job.cliente_id difiere de self.cliente_id.
        """
        if job.cliente_id != self.cliente_id:
            raise ValueError(
                f"cliente_id mismatch: repo={self.cliente_id!r}, "
                f"job={job.cliente_id!r}"
            )

        row = {
            "cliente_id": self.cliente_id,
            "job_id": job.job_id,
            "job_type": job.job_type,
            "status": str(job.status),
            "payload": job.payload or {},
            "result": job.result,
            "error_log": job.error_log,
            "traceable_origin": job.traceable_origin or {},
        }

        (
            self._client
            .table(_TABLE)
            .insert(row)
            .execute()
        )

    def get(self, job_id: str) -> Job | None:
        """Recupera un job por job_id, filtrado por cliente_id."""
        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("cliente_id", self.cliente_id)
            .eq("job_id", job_id)
            .execute()
        )

        rows = response.data
        if not rows:
            return None

        return self._row_to_job(rows[0])

    def list_jobs(self) -> list[Job]:
        """Lista todos los jobs del cliente_id. Nunca retorna jobs de otros clientes."""
        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("cliente_id", self.cliente_id)
            .execute()
        )

        return [self._row_to_job(row) for row in response.data]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_job(row: dict[str, Any]) -> Job:
        """Convierte una fila de Supabase a instancia de Job."""
        return Job(
            job_id=row["job_id"],
            cliente_id=row["cliente_id"],
            job_type=row["job_type"],
            status=JobStatus(row["status"]),
            payload=row.get("payload") or {},
            result=row.get("result"),
            error_log=row.get("error_log"),
            traceable_origin=row.get("traceable_origin") or {},
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
