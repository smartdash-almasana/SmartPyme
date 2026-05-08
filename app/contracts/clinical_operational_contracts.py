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
