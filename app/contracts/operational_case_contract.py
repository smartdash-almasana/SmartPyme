from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class OperationalCase:
    case_id: str
    cliente_id: str
    job_id: str
    skill_id: str
    demanda_original: str
    hypothesis: str
    taxonomia_pyme: dict[str, Any]
    variables_curadas: dict[str, Any]
    evidencia_disponible: list[str]
    condiciones_validadas: list[str]
    formula_applicable: str | None
    pathology_possible: str | None
    referencias_necesarias: list[str]
    investigation_plan: list[str]
    status: Literal["OPEN", "IN_PROGRESS", "CLOSED"]

    def __post_init__(self):
        if not self.case_id: raise ValueError("case_id required")
        if not self.cliente_id: raise ValueError("cliente_id required")
        if not self.job_id: raise ValueError("job_id required")
        if not self.hypothesis: raise ValueError("hypothesis required")
        
        # Simple heuristic: hypothesis should start with investigation verbs or contain ?
        h = self.hypothesis.lower()
        starts_valid = any(h.startswith(v) for v in ["investigar si", "analizar si", "determinar si", "verificar si", "evaluar si"])
        contains_q = "?" in h
        if not (starts_valid or contains_q):
            raise ValueError("HYPOTHESIS_INVALIDA: debe ser una pregunta o empezar con un verbo de investigacion (Investigar si...)")


@dataclass(frozen=True, slots=True)
class FindingRecord:
    entity: str
    finding_type: str
    measured_difference: dict[str, Any]
    compared_sources: list[str]
    evidence_used: list[str]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    recommendation: str

    def __post_init__(self):
        if not self.evidence_used:
            raise ValueError("EVIDENCE_USED_REQUERIDA: Un hallazgo debe tener evidencia vinculante.")


@dataclass(frozen=True, slots=True)
class QuantifiedImpact:
    amount: float | None = None
    currency: str | None = None
    percentage: float | None = None
    units: float | None = None
    time_saved: str | None = None
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] | None = None

    def __post_init__(self):
        # Check if at least one field is not None
        if all(v is None for v in [self.amount, self.currency, self.percentage, self.units, self.time_saved, self.risk_level]):
            raise ValueError("IMPACTO_VACIO: Al menos un campo de impacto debe estar presente.")


@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    report_id: str
    case_id: str
    cliente_id: str
    job_id: str
    hypothesis: str
    diagnosis_status: Literal["CONFIRMED", "NOT_CONFIRMED", "INSUFFICIENT_EVIDENCE"]
    findings: list[FindingRecord]
    evidence_used: list[str]
    formulas_used: list[str]
    quantified_impact: QuantifiedImpact
    reasoning_summary: str
    proposed_next_actions: list[str]
    owner_question: str

    def __post_init__(self):
        if self.diagnosis_status == "CONFIRMED":
            if not self.findings:
                raise ValueError("FINDINGS_REQUERIDOS: Un diagnostico CONFIRMED requiere hallazgos.")
            if not self.evidence_used:
                raise ValueError("EVIDENCE_REQUERIDA: Un diagnostico CONFIRMED requiere evidencia vinculante.")


@dataclass(frozen=True, slots=True)
class ValidatedCaseRecord:
    validated_case_id: str
    cliente_id: str
    job_id: str
    case_id: str
    report_id: str
    timestamp: str
    hypothesis: str
    diagnosis_status: str
    evidence_used: list[str]
    formulas_used: list[str]
    findings_summary: str
    quantified_impact: QuantifiedImpact
    owner_visible_report: str
    next_question: str
    metadata: dict[str, Any] = field(default_factory=dict)
