from __future__ import annotations

from typing import Any

from app.contracts.clinical_operational_contracts import (
    ClarificationRequest,
    Hypothesis,
    HypothesisNode,
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
        signal_nodes: list[dict[str, Any]] = []

        for signal in signals:
            evidence_ref = signal.evidence_refs[0]
            signal_node_id = self._build_signal_node_id(
                tenant_id=tenant_id.strip(),
                signal_type=signal.signal_type,
                evidence_ref=evidence_ref,
            )
            signal_nodes.append(
                {
                    "node_id": signal_node_id,
                    "tenant_id": tenant_id.strip(),
                    "signal_type": signal.signal_type,
                    "severity": signal.severity,
                    "evidence_refs": list(signal.evidence_refs),
                    "explanation": signal.explanation,
                    "status": "OBSERVED",
                }
            )

        supporting_signals = [
            signal.signal_type
            for signal in signals
            if signal.signal_type in _CRISIS_DE_MARGEN_SIGNAL_TYPES
        ]
        hypothesis_nodes: list[dict[str, Any]] = []
        if supporting_signals:
            hypothesis = Hypothesis(
                hypothesis_type="CRISIS_DE_MARGEN",
                confidence=0.60,
                supporting_signals=supporting_signals,
                requires_clarification=True,
            )
            hypotheses.append(hypothesis)
            clarification_requests.append(
                ClarificationRequest(
                    question=_CRISIS_DE_MARGEN_QUESTION,
                    related_hypothesis="CRISIS_DE_MARGEN",
                )
            )
            supporting_signal_node_ids = [
                node["node_id"]
                for node in signal_nodes
                if node["signal_type"] in set(supporting_signals)
            ]
            hypothesis_node = HypothesisNode(
                node_id=self._build_hypothesis_node_id(
                    tenant_id=tenant_id.strip(),
                    hypothesis_type=hypothesis.hypothesis_type,
                ),
                tenant_id=tenant_id.strip(),
                hypothesis_type=hypothesis.hypothesis_type,
                confidence=hypothesis.confidence,
                ambiguity=0.50,
                supporting_signals=list(hypothesis.supporting_signals),
                contradicting_signals=[],
                possible_explanations=[
                    "liquidacion_estrategica",
                    "error_de_costeo",
                    "precios_desactualizados",
                    "perdida_no_controlada",
                ],
                requires_clarification=hypothesis.requires_clarification,
                clarification_question=_CRISIS_DE_MARGEN_QUESTION,
                temporal_validity=None,
                status=(
                    "NEEDS_CLARIFICATION"
                    if hypothesis.requires_clarification
                    else "CANDIDATE"
                ),
            )
            node_payload = hypothesis_node.model_dump()
            node_payload["supporting_signal_node_ids"] = supporting_signal_node_ids
            hypothesis_nodes.append(node_payload)

        return {
            "signals": signals,
            "hypotheses": hypotheses,
            "clarification_requests": clarification_requests,
            "signal_nodes": signal_nodes,
            "hypothesis_nodes": hypothesis_nodes,
        }

    def _build_signal_node_id(
        self,
        *,
        tenant_id: str,
        signal_type: str,
        evidence_ref: str,
    ) -> str:
        return f"signal:{tenant_id}:{signal_type}:{evidence_ref}"

    def _build_hypothesis_node_id(
        self,
        *,
        tenant_id: str,
        hypothesis_type: str,
    ) -> str:
        return f"hypothesis:{tenant_id}:{hypothesis_type}"
