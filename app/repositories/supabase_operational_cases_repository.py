"""Adapter Supabase para operational_cases — SmartPyme P0.

Implementa OperationalCasePort usando un cliente Supabase inyectable.
El cliente real es `supabase.Client` (librería supabase-py).
En tests se inyecta un FakeSupabaseClient sin red.

Reglas:
    - cliente_id es OBLIGATORIO. Fail-closed si está vacío.
    - Todas las operaciones filtran por cliente_id.
    - create_case() rechaza mismatch entre case.cliente_id y self.cliente_id.
    - Si no se inyecta cliente explícito, se valida el entorno Supabase.
    - No modifica repositorios SQLite legacy.
    - No hace dual-write.
    - payload, result, metadata se insertan como dict/list (JSON-compatible),
      nunca como string si ya son dict/list.
    - job_id se conserva si existe en el caso.

Tabla Supabase esperada: operational_cases
    cliente_id      TEXT NOT NULL
    case_id         TEXT NOT NULL
    job_id          TEXT
    status          TEXT NOT NULL
    payload         JSONB
    result          JSONB
    metadata        JSONB
    created_at      TIMESTAMPTZ
    updated_at      TIMESTAMPTZ
    PRIMARY KEY (cliente_id, case_id)
"""
from __future__ import annotations

from typing import Any

from app.contracts.operational_case import OperationalCase
from app.repositories.persistence_provider import validate_supabase_env

_TABLE = "operational_cases"


class SupabaseOperationalCasesRepository:
    """Adapter Supabase para operational_cases. Implementa OperationalCasePort.

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
    # OperationalCasePort interface
    # ------------------------------------------------------------------

    def create_case(self, case: OperationalCase) -> None:
        """Persiste un nuevo caso operacional en Supabase.

        Fail-closed si case.cliente_id difiere de self.cliente_id.

        Args:
            case: Instancia de OperationalCase. case.cliente_id debe coincidir
                  con el cliente_id del adapter.

        Raises:
            ValueError: Si case.cliente_id difiere de self.cliente_id (mismatch).
        """
        if case.cliente_id != self.cliente_id:
            raise ValueError(
                f"cliente_id mismatch: repo={self.cliente_id!r}, "
                f"case={case.cliente_id!r}"
            )

        # payload: evidence_ids como lista JSON-compatible (no stringified).
        # metadata: dict vacío por defecto (OperationalCase no tiene campo metadata propio).
        row: dict[str, Any] = {
            "cliente_id": self.cliente_id,
            "case_id": case.case_id,
            "job_id": case.job_id if case.job_id else None,
            "status": str(case.status),
            "payload": {
                "skill_id": case.skill_id,
                "hypothesis": case.hypothesis,
                "evidence_ids": list(case.evidence_ids),
            },
            "result": None,
            "metadata": {},
        }

        (
            self._client
            .table(_TABLE)
            .insert(row)
            .execute()
        )

    def get_case(self, case_id: str) -> OperationalCase | None:
        """Recupera un caso por case_id, filtrado por cliente_id.

        Returns:
            Instancia de OperationalCase o None si no existe para este cliente.
        """
        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("cliente_id", self.cliente_id)
            .eq("case_id", case_id)
            .execute()
        )

        rows = response.data
        if not rows:
            return None

        return self._row_to_case(rows[0])

    def list_cases(self) -> list[OperationalCase]:
        """Lista todos los casos del cliente_id. Nunca retorna casos de otros clientes."""
        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("cliente_id", self.cliente_id)
            .execute()
        )

        return [self._row_to_case(row) for row in response.data]

    def update_case_status(self, case_id: str, status: str) -> bool:
        """Actualiza el estado de un caso, filtrado por cliente_id y case_id.

        Args:
            case_id: Identificador del caso.
            status: Nuevo estado.

        Returns:
            True si la actualización fue exitosa (fila encontrada y actualizada),
            False si el caso no existe para este cliente.
        """
        response = (
            self._client
            .table(_TABLE)
            .update({"status": status})
            .eq("cliente_id", self.cliente_id)
            .eq("case_id", case_id)
            .execute()
        )

        # Si data está vacío, no se encontró la fila para este cliente/case_id.
        return bool(response.data)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_case(row: dict[str, Any]) -> OperationalCase:
        """Convierte una fila de Supabase a instancia de OperationalCase.

        El payload almacenado contiene: skill_id, hypothesis, evidence_ids.
        """
        payload = row.get("payload") or {}

        return OperationalCase(
            cliente_id=row["cliente_id"],
            case_id=row["case_id"],
            job_id=row.get("job_id") or "",
            skill_id=payload.get("skill_id", ""),
            hypothesis=payload.get("hypothesis", ""),
            evidence_ids=list(payload.get("evidence_ids") or []),
            status=row["status"],
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
