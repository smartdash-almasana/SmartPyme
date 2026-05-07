"""Adapter Supabase para decisions (decision_records) — SmartPyme P0.

Implementa DecisionPort usando un cliente Supabase inyectable.
El cliente real es `supabase.Client` (librería supabase-py).
En tests se inyecta un FakeSupabaseClient sin red.

Mapeo de campos DecisionRecord → columnas tabla decisions:
    decision_id     → decision_id
    cliente_id      → cliente_id
    tipo_decision   → decision_type
    accion          → decision_value
    propuesta       → rationale (JSONB)
    overrides       → metadata (JSONB, puede ser None → {})
    job_id          → conservado en metadata["job_id"]
    case_id         → case_id (si se provee en kwargs o metadata)
    report_id       → report_id (si se provee en kwargs o metadata)
    timestamp       → metadata["timestamp"]
    mensaje_original → metadata["mensaje_original"]

Reglas:
    - cliente_id es OBLIGATORIO. Fail-closed si está vacío.
    - Todas las operaciones filtran por cliente_id.
    - create() rechaza mismatch entre decision.cliente_id y self.cliente_id.
    - Si no se inyecta cliente explícito, se valida el entorno Supabase.
    - No modifica repositorios SQLite legacy.
    - No hace dual-write.
    - rationale y metadata se insertan como dict (JSON-compatible), nunca stringified.
    - case_id y report_id se conservan si existen en la entidad.

Tabla Supabase esperada: decisions
    cliente_id      TEXT NOT NULL
    decision_id     TEXT NOT NULL
    case_id         TEXT
    report_id       TEXT
    decision_type   TEXT NOT NULL
    decision_value  TEXT
    rationale       JSONB
    metadata        JSONB
    created_at      TIMESTAMPTZ
    updated_at      TIMESTAMPTZ
    PRIMARY KEY (cliente_id, decision_id)
"""
from __future__ import annotations

from typing import Any

from app.contracts.decision_record import DecisionRecord
from app.repositories.persistence_provider import validate_supabase_env

_TABLE = "decisions"


class SupabaseDecisionsRepository:
    """Adapter Supabase para decisions. Implementa DecisionPort.

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
    # DecisionPort interface
    # ------------------------------------------------------------------

    def create(self, decision: DecisionRecord) -> None:
        """Persiste una nueva decisión en Supabase.

        Fail-closed si decision.cliente_id difiere de self.cliente_id.

        Args:
            decision: Instancia de DecisionRecord. decision.cliente_id debe
                      coincidir con el cliente_id del adapter.

        Raises:
            ValueError: Si decision.cliente_id difiere de self.cliente_id (mismatch).
        """
        if decision.cliente_id != self.cliente_id:
            raise ValueError(
                f"cliente_id mismatch: repo={self.cliente_id!r}, "
                f"decision={decision.cliente_id!r}"
            )

        # Extraer case_id y report_id desde overrides si están presentes.
        overrides = decision.overrides or {}
        case_id = overrides.get("case_id") or None
        report_id = overrides.get("report_id") or None

        # metadata: preserva campos auxiliares del DecisionRecord.
        metadata: dict[str, Any] = {
            "timestamp": decision.timestamp,
            "mensaje_original": decision.mensaje_original,
        }
        if decision.job_id:
            metadata["job_id"] = decision.job_id
        # Incluir overrides restantes (sin case_id/report_id ya extraídos).
        remaining_overrides = {
            k: v for k, v in overrides.items()
            if k not in ("case_id", "report_id")
        }
        if remaining_overrides:
            metadata["overrides"] = remaining_overrides

        row: dict[str, Any] = {
            "cliente_id": self.cliente_id,
            "decision_id": decision.decision_id,
            "case_id": case_id,
            "report_id": report_id,
            "decision_type": decision.tipo_decision,
            "decision_value": decision.accion,
            "rationale": dict(decision.propuesta) if decision.propuesta else {},
            "metadata": metadata,
        }

        (
            self._client
            .table(_TABLE)
            .insert(row)
            .execute()
        )

    def get(self, decision_id: str) -> DecisionRecord | None:
        """Recupera una decisión por decision_id, filtrado por cliente_id.

        Returns:
            Instancia de DecisionRecord o None si no existe para este cliente.
        """
        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("cliente_id", self.cliente_id)
            .eq("decision_id", decision_id)
            .execute()
        )

        rows = response.data
        if not rows:
            return None

        return self._row_to_decision(rows[0])

    def list_decisions(self) -> list[DecisionRecord]:
        """Lista todas las decisiones del cliente_id. Nunca retorna decisiones de otros clientes."""
        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("cliente_id", self.cliente_id)
            .execute()
        )

        return [self._row_to_decision(row) for row in response.data]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_decision(row: dict[str, Any]) -> DecisionRecord:
        """Convierte una fila de Supabase a instancia de DecisionRecord.

        Reconstruye los campos auxiliares desde metadata y rationale.
        case_id y report_id se reinyectan en overrides para trazabilidad.
        """
        metadata = row.get("metadata") or {}
        rationale = row.get("rationale") or {}

        # Reconstruir overrides: case_id + report_id + overrides residuales.
        overrides: dict[str, Any] = {}
        if row.get("case_id"):
            overrides["case_id"] = row["case_id"]
        if row.get("report_id"):
            overrides["report_id"] = row["report_id"]
        residual = metadata.get("overrides") or {}
        overrides.update(residual)

        return DecisionRecord(
            decision_id=row["decision_id"],
            cliente_id=row["cliente_id"],
            timestamp=metadata.get("timestamp", ""),
            tipo_decision=row["decision_type"],
            mensaje_original=metadata.get("mensaje_original", ""),
            propuesta=dict(rationale),
            accion=row.get("decision_value") or "",
            overrides=overrides if overrides else None,
            job_id=metadata.get("job_id"),
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
