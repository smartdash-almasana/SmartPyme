from __future__ import annotations

import hashlib
import json
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
        report_id: str | None = None,
    ) -> DiagnosticReport:
        """Genera un DiagnosticReport manteniendo cliente_id, case_id e hypothesis del caso.

        Args:
            operational_case: El caso operativo (Capa 03) que dio origen a la investigación.
            evidence_used: Lista de identificadores de evidencia utilizada en el diagnóstico.
            findings: Lista de hallazgos estructurados (dicts).
            diagnosis_status: Estado del diagnóstico (CONFIRMED, NOT_CONFIRMED, INSUFFICIENT_EVIDENCE).
            report_id: Identificador opcional. Si no se informa, se genera de forma determinística.

        Returns:
            DiagnosticReport: El reporte construido.

        Raises:
            ValueError: Si diagnosis_status es CONFIRMED pero evidence_used o findings están vacíos.
        """
        if diagnosis_status == "CONFIRMED":
            if not evidence_used:
                raise ValueError("CONFIRMED diagnosis requires non-empty evidence_used")
            if not findings:
                raise ValueError("CONFIRMED diagnosis requires non-empty findings")

        resolved_report_id = report_id or cls._build_deterministic_report_id(
            operational_case=operational_case,
            evidence_used=evidence_used,
            findings=findings,
            diagnosis_status=diagnosis_status,
        )

        reasoning_summary = (
            f"Reporte generado para hipótesis: {operational_case.hypothesis}. "
            f"Estado diagnóstico: {diagnosis_status}."
        )

        return DiagnosticReport(
            cliente_id=operational_case.cliente_id,
            report_id=resolved_report_id,
            case_id=operational_case.case_id,
            hypothesis=operational_case.hypothesis,
            diagnosis_status=diagnosis_status,
            findings=findings,
            evidence_used=evidence_used,
            reasoning_summary=reasoning_summary,
        )

    @staticmethod
    def _build_deterministic_report_id(
        operational_case: OperationalCase,
        evidence_used: list[str],
        findings: list[dict[str, Any]],
        diagnosis_status: DiagnosisStatus,
    ) -> str:
        payload = {
            "cliente_id": operational_case.cliente_id,
            "case_id": operational_case.case_id,
            "hypothesis": operational_case.hypothesis,
            "diagnosis_status": diagnosis_status,
            "evidence_used": evidence_used,
            "findings": findings,
        }
        canonical_payload = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()[:16]
        return f"dr_{digest}"
