from __future__ import annotations

from typing import Any

from app.contracts.clinical_operational_contracts import (
    ClarificationRequest,
    Hypothesis,
    Signal,
)

_CRISIS_DE_MARGEN_SIGNAL_TYPES = {
    "VENTA_BAJO_COSTO",
    "RENTABILIDAD_NULA",
    "MARGEN_CRITICO",
    "COSTO_CERO_SOSPECHOSO",
    "DESCUENTO_EXCESIVO",
    "PRECIO_DESACTUALIZADO",
}

_CRISIS_DE_MARGEN_QUESTION = (
    "Detecté señales de crisis de margen. ¿Esto corresponde a una liquidación "
    "estratégica, error de costeo, precios desactualizados o pérdida no controlada?"
)


class ClinicalOperationalMapper:
    def map_report(self, report: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(report, dict):
            raise TypeError("report debe ser dict")
        tenant_id = report.get("tenant_id")
        findings = report.get("findings")
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant_id es obligatorio y no puede estar vacío")
        if not isinstance(findings, list):
            raise ValueError("findings debe ser lista")

        signals: list[Signal] = []
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            signal_type = finding.get("finding_type")
            severity = finding.get("severity")
            message = finding.get("message")
            evidence_id = finding.get("evidence_id")
            if not isinstance(signal_type, str) or not signal_type.strip():
                continue
            if not isinstance(severity, str) or not severity.strip():
                continue
            if not isinstance(message, str) or not message.strip():
                continue
            if not isinstance(evidence_id, str) or not evidence_id.strip():
                continue
            signals.append(
                Signal(
                    signal_type=signal_type,
                    severity=severity,
                    evidence_refs=[evidence_id],
                    explanation=message,
                )
            )

        hypotheses: list[Hypothesis] = []
        clarification_requests: list[ClarificationRequest] = []

        supporting_signals = [
            signal.signal_type
            for signal in signals
            if signal.signal_type in _CRISIS_DE_MARGEN_SIGNAL_TYPES
        ]
        if supporting_signals:
            hypotheses.append(
                Hypothesis(
                    hypothesis_type="CRISIS_DE_MARGEN",
                    confidence=0.60,
                    supporting_signals=supporting_signals,
                    requires_clarification=True,
                )
            )
            clarification_requests.append(
                ClarificationRequest(
                    question=_CRISIS_DE_MARGEN_QUESTION,
                    related_hypothesis="CRISIS_DE_MARGEN",
                )
            )

        return {
            "signals": signals,
            "hypotheses": hypotheses,
            "clarification_requests": clarification_requests,
        }
