"""Adapter Supabase para reports (diagnostic_reports) — SmartPyme P0.

Implementa ReportPort usando un cliente Supabase inyectable.
El cliente real es `supabase.Client` (librería supabase-py).
En tests se inyecta un FakeSupabaseClient sin red.

Reglas:
    - cliente_id es OBLIGATORIO. Fail-closed si está vacío.
    - Todas las operaciones filtran por cliente_id.
    - create_report() rechaza mismatch entre report.cliente_id y self.cliente_id.
    - Si no se inyecta cliente explícito, se valida el entorno Supabase.
    - No modifica repositorios SQLite legacy.
    - No hace dual-write.
    - No persiste LaboratorioReportDraft como entidad paralela.
    - payload, result, metadata se insertan como dict/list (JSON-compatible),
      nunca como string si ya son dict/list.
    - case_id y job_id se conservan si existen en el reporte.

Tabla Supabase esperada: reports
    cliente_id      TEXT NOT NULL
    report_id       TEXT NOT NULL
    case_id         TEXT
    job_id          TEXT
    status          TEXT NOT NULL DEFAULT 'draft'
    payload         JSONB
    result          JSONB
    metadata        JSONB
    created_at      TIMESTAMPTZ
    updated_at      TIMESTAMPTZ
    PRIMARY KEY (cliente_id, report_id)
"""
from __future__ import annotations

from typing import Any

from app.contracts.diagnostic_report import DiagnosticReport
from app.repositories.persistence_provider import validate_supabase_env

_TABLE = "reports"


class SupabaseReportsRepository:
    """Adapter Supabase para reports. Implementa ReportPort.

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
    # ReportPort interface
    # ------------------------------------------------------------------

    def create_report(self, report: DiagnosticReport) -> None:
        """Persiste un nuevo reporte diagnóstico en Supabase.

        Fail-closed si report.cliente_id difiere de self.cliente_id.

        Args:
            report: Instancia de DiagnosticReport. report.cliente_id debe
                    coincidir con el cliente_id del adapter.

        Raises:
            ValueError: Si report.cliente_id difiere de self.cliente_id (mismatch).
        """
        if report.cliente_id != self.cliente_id:
            raise ValueError(
                f"cliente_id mismatch: repo={self.cliente_id!r}, "
                f"report={report.cliente_id!r}"
            )

        row: dict[str, Any] = {
            "cliente_id": self.cliente_id,
            "report_id": report.report_id,
            "case_id": report.case_id if report.case_id else None,
            "job_id": None,  # DiagnosticReport no tiene job_id propio; reservado para extensión
            "status": report.diagnosis_status,
            "payload": {
                "hypothesis": report.hypothesis,
                "findings": list(report.findings),
                "evidence_used": list(report.evidence_used),
                "reasoning_summary": report.reasoning_summary,
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

    def get_report(self, report_id: str) -> DiagnosticReport | None:
        """Recupera un reporte por report_id, filtrado por cliente_id.

        Returns:
            Instancia de DiagnosticReport o None si no existe para este cliente.
        """
        response = (
            self._client
            .table(_TABLE)
            .select("*")
            .eq("cliente_id", self.cliente_id)
            .eq("report_id", report_id)
            .execute()
        )

        rows = response.data
        if not rows:
            return None

        return self._row_to_report(rows[0])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_report(row: dict[str, Any]) -> DiagnosticReport:
        """Convierte una fila de Supabase a instancia de DiagnosticReport.

        El payload almacenado contiene: hypothesis, findings, evidence_used,
        reasoning_summary.
        """
        payload = row.get("payload") or {}

        return DiagnosticReport(
            cliente_id=row["cliente_id"],
            report_id=row["report_id"],
            case_id=row.get("case_id") or "",
            hypothesis=payload.get("hypothesis", ""),
            diagnosis_status=row["status"],
            findings=list(payload.get("findings") or []),
            evidence_used=list(payload.get("evidence_used") or []),
            reasoning_summary=payload.get("reasoning_summary", ""),
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
