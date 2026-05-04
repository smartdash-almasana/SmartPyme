from __future__ import annotations

import uuid
from typing import Any

from app.contracts.diagnostic_report import DiagnosticReport, DiagnosisStatus
from app.contracts.operational_case import OperationalCase


class DiagnosticService:
    """Servicio mínimo para crear DiagnosticReport a partir de un OperationalCase.

    No ejecuta acciones, no autoriza, no diagnostica por IA.
    Solo construye el reporte con datos recibidos y valida reglas de consistencia.
    """

    @classmethod
    def generate_report(
        cls,
        operational_case: OperationalCase,
        evidence_used: list[str],
        findings: list[dict[str, Any]],
        diagnosis_status: DiagnosisStatus,
    ) -> DiagnosticReport:
        """Genera un DiagnosticReport manteniendo cliente_id, case_id e hypothesis del caso.

        Args:
            operational_case: El caso operativo (Capa 03) que dio origen a la investigación.
            evidence_used: Lista de identificadores de evidencia utilizada en el diagnóstico.
            findings: Lista de hallazgos estructurados (dicts).
            diagnosis_status: Estado del diagnóstico (CONFIRMED, NOT_CONFIRMED, INSUFFICIENT_EVIDENCE).

        Returns:
            DiagnosticReport: El reporte construido.

        Raises:
            ValueError: Si diagnosis_status es CONFIRMED pero evidence_used o findings están vacíos.
        """
        if diagnosis_status == "CONFIRMED":
            if not evidence_used:
                raise ValueError("CONFIRMED diagnosis requires non‑empty evidence_used")
            if not findings:
                raise ValueError("CONFIRMED diagnosis requires non‑empty findings")

        # Generar un ID único para el reporte
        report_id = f"dr_{uuid.uuid4().hex[:12]}"

        # Para INSUFFICIENT_EVIDENCE, permitir evidence_used y findings vacíos
        # (ya que el estado refleja precisamente falta de evidencia).
        # Para NOT_CONFIRMED también se permiten vacíos (el diagnóstico no pudo confirmarse).

        # Construir reasoning_summary básico a partir de la hypothesis
        reasoning_summary = (
            f"Reporte generado para hipótesis: {operational_case.hypothesis}. "
            f"Estado diagnóstico: {diagnosis_status}."
        )

        return DiagnosticReport(
            cliente_id=operational_case.cliente_id,
            report_id=report_id,
            case_id=operational_case.case_id,
            hypothesis=operational_case.hypothesis,
            diagnosis_status=diagnosis_status,
            findings=findings,
            evidence_used=evidence_used,
            reasoning_summary=reasoning_summary,
        )