"""Contratos base clinico-operacionales SmartPyme.

Regla rectora:
IA interpreta.
Deterministico decide.
Evidencia gobierna.
Dueno confirma.

Este modulo define contratos minimos de admision y evidencia.
No contiene logica de diagnostico ni hallazgos finales.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


ReceptionStatus = Literal[
    "RECEIVED",
    "CLASSIFIED",
    "NEEDS_EVIDENCE",
    "READY_TO_PROCESS",
    "PROCESSING",
    "DELIVERED",
    "BLOCKED",
    "UNSUPPORTED",
]

EvidenceSourceType = Literal[
    "excel",
    "pdf",
    "image",
    "text",
    "email",
    "whatsapp",
    "manual",
    "other",
]

EvidenceStatus = Literal[
    "RECEIVED",
    "STRUCTURED",
    "NEEDS_REVIEW",
    "REJECTED",
    "LINKED",
]

IngestionProvider = Literal["bem", "manual", "internal", "other"]

IngestionStatus = Literal[
    "RECEIVED",
    "SENT_TO_PROVIDER",
    "STRUCTURED",
    "NEEDS_REVIEW",
    "FAILED",
    "REJECTED",
]

ObservationStatus = Literal["OBSERVED", "NEEDS_REVIEW", "REJECTED", "CONFIRMED"]

PathologyCandidateStatus = Literal[
    "CANDIDATE",
    "NEEDS_EVIDENCE",
    "READY_FOR_EVALUATION",
    "REJECTED",
]

FormulaExecutionStatus = Literal["READY", "EXECUTED", "BLOCKED", "FAILED"]

OperationalCaseCandidateStatus = Literal[
    "DRAFT",
    "NEEDS_EVIDENCE",
    "READY_FOR_REVIEW",
    "REJECTED",
]

OperationalCaseStatus = Literal[
    "READY_FOR_INVESTIGATION",
    "CLARIFICATION_REQUIRED",
    "INSUFFICIENT_EVIDENCE",
    "REJECTED_OUT_OF_SCOPE",
]

FindingSeverity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
FindingStatus = Literal["DRAFT", "SUPPORTED", "NEEDS_REVIEW", "REJECTED"]


class ReceptionRecord(BaseModel):
    reception_id: str = Field(...)
    tenant_id: str = Field(...)
    channel: str = Field(...)
    original_message: str = Field(...)
    expressed_pain: str | None = Field(default=None)
    initial_classification: str | None = Field(default=None)
    status: ReceptionStatus = Field(...)
    requested_evidence_ids: list[str] = Field(default_factory=list)
    received_evidence_ids: list[str] = Field(default_factory=list)
    result_id: str | None = Field(default=None)
    blocking_reason: str | None = Field(default=None)
    detected_opportunity: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _validate_rules(self) -> "ReceptionRecord":
        if not self.tenant_id or not self.tenant_id.strip():
            raise ValueError("tenant_id no puede ser vacio")

        if not self.original_message or not self.original_message.strip():
            raise ValueError("original_message no puede ser vacio")

        if self.status == "BLOCKED":
            if not self.blocking_reason or not self.blocking_reason.strip():
                raise ValueError("blocking_reason es obligatorio cuando status == BLOCKED")

        if self.status == "NEEDS_EVIDENCE":
            if not self.requested_evidence_ids:
                raise ValueError(
                    "requested_evidence_ids debe tener al menos un item cuando status == NEEDS_EVIDENCE"
                )

        return self


class EvidenceRecord(BaseModel):
    evidence_id: str = Field(...)
    tenant_id: str = Field(...)
    source_type: EvidenceSourceType = Field(...)
    source_name: str | None = Field(default=None)
    received_from: str | None = Field(default=None)
    storage_ref: str | None = Field(default=None)
    content_hash: str | None = Field(default=None)
    status: EvidenceStatus = Field(...)
    linked_reception_id: str | None = Field(default=None)
    quality_flags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _validate_rules(self) -> "EvidenceRecord":
        if not self.tenant_id or not self.tenant_id.strip():
            raise ValueError("tenant_id no puede ser vacio")

        if not self.evidence_id or not self.evidence_id.strip():
            raise ValueError("evidence_id no puede ser vacio")

        if self.status == "LINKED":
            if not self.linked_reception_id or not self.linked_reception_id.strip():
                raise ValueError("linked_reception_id es obligatorio cuando status == LINKED")

        if self.status == "REJECTED":
            if not self.quality_flags:
                raise ValueError("quality_flags debe tener al menos un item cuando status == REJECTED")

        return self


class DocumentIngestion(BaseModel):
    ingestion_id: str = Field(...)
    tenant_id: str = Field(...)
    evidence_id: str = Field(...)
    provider: IngestionProvider = Field(...)
    source_type: EvidenceSourceType = Field(...)
    status: IngestionStatus = Field(...)
    provider_workflow_id: str | None = Field(default=None)
    provider_call_id: str | None = Field(default=None)
    output_ref: str | None = Field(default=None)
    error_message: str | None = Field(default=None)
    quality_flags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _validate_rules(self) -> "DocumentIngestion":
        if not self.ingestion_id or not self.ingestion_id.strip():
            raise ValueError("ingestion_id no puede ser vacio")
        if not self.tenant_id or not self.tenant_id.strip():
            raise ValueError("tenant_id no puede ser vacio")
        if not self.evidence_id or not self.evidence_id.strip():
            raise ValueError("evidence_id no puede ser vacio")

        if self.provider == "bem" and self.status in {"SENT_TO_PROVIDER", "STRUCTURED", "NEEDS_REVIEW"}:
            if not self.provider_call_id or not self.provider_call_id.strip():
                raise ValueError(
                    "provider_call_id es obligatorio para provider == bem en estados SENT_TO_PROVIDER/STRUCTURED/NEEDS_REVIEW"
                )

        if self.status == "STRUCTURED":
            if not self.output_ref or not self.output_ref.strip():
                raise ValueError("output_ref es obligatorio cuando status == STRUCTURED")

        if self.status == "FAILED":
            if not self.error_message or not self.error_message.strip():
                raise ValueError("error_message es obligatorio cuando status == FAILED")

        if self.status == "REJECTED":
            if not self.quality_flags:
                raise ValueError("quality_flags debe tener al menos un item cuando status == REJECTED")

        return self


class VariableObservation(BaseModel):
    observation_id: str = Field(...)
    tenant_id: str = Field(...)
    variable_code: str = Field(...)
    value: str | int | float | bool | None = Field(default=None)
    unit: str | None = Field(default=None)
    period: str | None = Field(default=None)
    evidence_id: str = Field(...)
    ingestion_id: str | None = Field(default=None)
    source_ref: str | None = Field(default=None)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    status: ObservationStatus = Field(...)
    quality_flags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _validate_rules(self) -> "VariableObservation":
        if not self.observation_id or not self.observation_id.strip():
            raise ValueError("observation_id no puede ser vacio")
        if not self.tenant_id or not self.tenant_id.strip():
            raise ValueError("tenant_id no puede ser vacio")
        if not self.variable_code or not self.variable_code.strip():
            raise ValueError("variable_code no puede ser vacio")
        if not self.evidence_id or not self.evidence_id.strip():
            raise ValueError("evidence_id no puede ser vacio")

        if self.status == "CONFIRMED" and self.value is None:
            raise ValueError("value es obligatorio cuando status == CONFIRMED")

        if self.status == "REJECTED" and not self.quality_flags:
            raise ValueError("quality_flags debe tener al menos un item cuando status == REJECTED")

        return self


class PathologyCandidate(BaseModel):
    candidate_id: str = Field(...)
    tenant_id: str = Field(...)
    pathology_code: str = Field(...)
    source_reception_id: str | None = Field(default=None)
    symptom_codes: list[str] = Field(default_factory=list)
    supporting_observation_ids: list[str] = Field(default_factory=list)
    missing_evidence_codes: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    status: PathologyCandidateStatus = Field(...)
    rejection_reason: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _validate_rules(self) -> "PathologyCandidate":
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("candidate_id no puede ser vacio")
        if not self.tenant_id or not self.tenant_id.strip():
            raise ValueError("tenant_id no puede ser vacio")
        if not self.pathology_code or not self.pathology_code.strip():
            raise ValueError("pathology_code no puede ser vacio")

        if self.status == "NEEDS_EVIDENCE" and not self.missing_evidence_codes:
            raise ValueError(
                "missing_evidence_codes debe tener al menos un item cuando status == NEEDS_EVIDENCE"
            )

        if self.status == "READY_FOR_EVALUATION" and not self.supporting_observation_ids:
            raise ValueError(
                "supporting_observation_ids debe tener al menos un item cuando status == READY_FOR_EVALUATION"
            )

        if self.status == "REJECTED":
            if not self.rejection_reason or not self.rejection_reason.strip():
                raise ValueError("rejection_reason es obligatorio cuando status == REJECTED")

        return self


class FormulaExecution(BaseModel):
    execution_id: str = Field(...)
    tenant_id: str = Field(...)
    formula_code: str = Field(...)
    input_observation_ids: list[str] = Field(default_factory=list)
    output_variable_code: str | None = Field(default=None)
    result_value: str | int | float | bool | None = Field(default=None)
    result_unit: str | None = Field(default=None)
    status: FormulaExecutionStatus = Field(...)
    blocking_reason: str | None = Field(default=None)
    error_message: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _validate_rules(self) -> "FormulaExecution":
        if not self.execution_id or not self.execution_id.strip():
            raise ValueError("execution_id no puede ser vacio")
        if not self.tenant_id or not self.tenant_id.strip():
            raise ValueError("tenant_id no puede ser vacio")
        if not self.formula_code or not self.formula_code.strip():
            raise ValueError("formula_code no puede ser vacio")

        if self.status in {"READY", "EXECUTED"} and not self.input_observation_ids:
            raise ValueError(
                "input_observation_ids debe tener al menos un item cuando status == READY o EXECUTED"
            )

        if self.status == "EXECUTED" and self.result_value is None:
            raise ValueError("result_value es obligatorio cuando status == EXECUTED")

        if self.status == "BLOCKED":
            if not self.blocking_reason or not self.blocking_reason.strip():
                raise ValueError("blocking_reason es obligatorio cuando status == BLOCKED")

        if self.status == "FAILED":
            if not self.error_message or not self.error_message.strip():
                raise ValueError("error_message es obligatorio cuando status == FAILED")

        return self


class OperationalCaseCandidate(BaseModel):
    candidate_id: str = Field(...)
    tenant_id: str = Field(...)
    source_reception_id: str = Field(...)
    pathology_candidate_ids: list[str] = Field(default_factory=list)
    variable_observation_ids: list[str] = Field(default_factory=list)
    formula_execution_ids: list[str] = Field(default_factory=list)
    primary_pathology_code: str | None = Field(default=None)
    evidence_gap_codes: list[str] = Field(default_factory=list)
    principal_entropic_core: str | None = Field(default=None)
    recommended_route: str | None = Field(default=None)
    status: OperationalCaseCandidateStatus = Field(...)
    rejection_reason: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _validate_rules(self) -> "OperationalCaseCandidate":
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("candidate_id no puede ser vacio")
        if not self.tenant_id or not self.tenant_id.strip():
            raise ValueError("tenant_id no puede ser vacio")
        if not self.source_reception_id or not self.source_reception_id.strip():
            raise ValueError("source_reception_id no puede ser vacio")

        if self.status == "NEEDS_EVIDENCE" and not self.evidence_gap_codes:
            raise ValueError(
                "evidence_gap_codes debe tener al menos un item cuando status == NEEDS_EVIDENCE"
            )

        if self.status == "READY_FOR_REVIEW":
            if not self.pathology_candidate_ids:
                raise ValueError(
                    "pathology_candidate_ids debe tener al menos un item cuando status == READY_FOR_REVIEW"
                )
            if not self.variable_observation_ids:
                raise ValueError(
                    "variable_observation_ids debe tener al menos un item cuando status == READY_FOR_REVIEW"
                )
            if not self.formula_execution_ids:
                raise ValueError(
                    "formula_execution_ids debe tener al menos un item cuando status == READY_FOR_REVIEW"
                )
            if not self.primary_pathology_code or not self.primary_pathology_code.strip():
                raise ValueError(
                    "primary_pathology_code es obligatorio cuando status == READY_FOR_REVIEW"
                )
            if not self.principal_entropic_core or not self.principal_entropic_core.strip():
                raise ValueError(
                    "principal_entropic_core es obligatorio cuando status == READY_FOR_REVIEW"
                )

        if self.status == "REJECTED":
            if not self.rejection_reason or not self.rejection_reason.strip():
                raise ValueError("rejection_reason es obligatorio cuando status == REJECTED")

        return self


class OperationalCase(BaseModel):
    case_id: str = Field(...)
    tenant_id: str = Field(...)
    candidate_id: str = Field(...)
    source_reception_id: str = Field(...)
    primary_pathology_code: str = Field(...)
    related_pathology_codes: list[str] = Field(default_factory=list)
    formula_execution_ids: list[str] = Field(default_factory=list)
    variable_observation_ids: list[str] = Field(default_factory=list)
    evidence_gap_codes: list[str] = Field(default_factory=list)
    principal_entropic_core: str | None = Field(default=None)
    recommended_route: str | None = Field(default=None)
    status: OperationalCaseStatus = Field(...)
    clarification_question: str | None = Field(default=None)
    insufficiency_reason: str | None = Field(default=None)
    rejection_reason: str | None = Field(default=None)
    next_step: str = Field(...)
    opened_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _validate_rules(self) -> "OperationalCase":
        if not self.case_id or not self.case_id.strip():
            raise ValueError("case_id no puede ser vacio")
        if not self.tenant_id or not self.tenant_id.strip():
            raise ValueError("tenant_id no puede ser vacio")
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("candidate_id no puede ser vacio")
        if not self.source_reception_id or not self.source_reception_id.strip():
            raise ValueError("source_reception_id no puede ser vacio")
        if not self.primary_pathology_code or not self.primary_pathology_code.strip():
            raise ValueError("primary_pathology_code no puede ser vacio")
        if not self.next_step or not self.next_step.strip():
            raise ValueError("next_step no puede ser vacio")

        if self.status == "READY_FOR_INVESTIGATION":
            if not self.variable_observation_ids:
                raise ValueError(
                    "variable_observation_ids debe tener al menos un item cuando status == READY_FOR_INVESTIGATION"
                )
            if not self.formula_execution_ids:
                raise ValueError(
                    "formula_execution_ids debe tener al menos un item cuando status == READY_FOR_INVESTIGATION"
                )
            if not self.principal_entropic_core or not self.principal_entropic_core.strip():
                raise ValueError(
                    "principal_entropic_core es obligatorio cuando status == READY_FOR_INVESTIGATION"
                )
            if self.opened_at is None:
                raise ValueError("opened_at es obligatorio cuando status == READY_FOR_INVESTIGATION")

        if self.status == "CLARIFICATION_REQUIRED":
            if not self.clarification_question or not self.clarification_question.strip():
                raise ValueError(
                    "clarification_question es obligatorio cuando status == CLARIFICATION_REQUIRED"
                )

        if self.status == "INSUFFICIENT_EVIDENCE":
            if not self.insufficiency_reason or not self.insufficiency_reason.strip():
                raise ValueError(
                    "insufficiency_reason es obligatorio cuando status == INSUFFICIENT_EVIDENCE"
                )

        if self.status == "REJECTED_OUT_OF_SCOPE":
            if not self.rejection_reason or not self.rejection_reason.strip():
                raise ValueError(
                    "rejection_reason es obligatorio cuando status == REJECTED_OUT_OF_SCOPE"
                )

        return self


class FindingRecord(BaseModel):
    finding_id: str = Field(...)
    tenant_id: str = Field(...)
    case_id: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    severity: FindingSeverity = Field(...)
    status: FindingStatus = Field(...)
    evidence_ids: list[str] = Field(default_factory=list)
    variable_observation_ids: list[str] = Field(default_factory=list)
    formula_execution_ids: list[str] = Field(default_factory=list)
    quantified_difference: str | int | float | None = Field(default=None)
    comparison_summary: str | None = Field(default=None)
    recommended_next_step: str | None = Field(default=None)
    human_review_required: bool = Field(default=False)
    rejection_reason: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def _validate_rules(self) -> "FindingRecord":
        if not self.finding_id or not self.finding_id.strip():
            raise ValueError("finding_id no puede ser vacio")
        if not self.tenant_id or not self.tenant_id.strip():
            raise ValueError("tenant_id no puede ser vacio")
        if not self.case_id or not self.case_id.strip():
            raise ValueError("case_id no puede ser vacio")
        if not self.title or not self.title.strip():
            raise ValueError("title no puede ser vacio")
        if not self.description or not self.description.strip():
            raise ValueError("description no puede ser vacio")

        if self.status == "SUPPORTED":
            if not self.evidence_ids:
                raise ValueError("evidence_ids debe tener al menos un item cuando status == SUPPORTED")

            if not self.variable_observation_ids and not self.formula_execution_ids:
                raise ValueError(
                    "variable_observation_ids o formula_execution_ids debe tener al menos un item cuando status == SUPPORTED"
                )

            if not self.comparison_summary or not self.comparison_summary.strip():
                raise ValueError(
                    "comparison_summary es obligatorio cuando status == SUPPORTED"
                )

            if self.quantified_difference is None and (
                not self.comparison_summary or not self.comparison_summary.strip()
            ):
                raise ValueError(
                    "quantified_difference o comparison_summary debe existir cuando status == SUPPORTED"
                )

        if self.severity == "CRITICAL" and self.human_review_required is not True:
            raise ValueError("human_review_required debe ser True cuando severity == CRITICAL")

        if self.status == "REJECTED":
            if not self.rejection_reason or not self.rejection_reason.strip():
                raise ValueError("rejection_reason es obligatorio cuando status == REJECTED")

        return self
