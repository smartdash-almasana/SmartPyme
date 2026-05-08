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
