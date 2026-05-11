"""Contratos minimos de SmartGraph clinico-operacional.

SmartGraph modela relaciones clinico-operacionales sin introducir todavia
Neo4j, embeddings ni inferencia probabilistica completa.

Reglas rectoras:
- IA interpreta; kernel decide.
- La duda se sostiene como hipotesis auditable.
- El criterio del dueno reduce ambiguedad, no reemplaza evidencia.
- El cuadro operacional estabiliza senales e hipotesis, no ejecuta acciones.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


SmartGraphNodeStatus = Literal[
    "OBSERVED",
    "CANDIDATE",
    "NEEDS_CLARIFICATION",
    "OWNER_CERTIFIED",
    "STABILIZED",
    "REJECTED",
]

SignalNodeKind = Literal[
    "finding_signal",
    "computed_signal",
    "owner_signal",
    "temporal_signal",
]

HypothesisNodeStatus = Literal[
    "CANDIDATE",
    "NEEDS_CLARIFICATION",
    "SUPPORTED",
    "REJECTED",
]

OwnerCriterionNodeStatus = Literal[
    "CAPTURED",
    "APPLIED",
    "SUPERSEDED",
    "REJECTED",
]

OperationalPictureNodeStatus = Literal[
    "DRAFT",
    "NEEDS_CLARIFICATION",
    "STABILIZED",
    "REJECTED",
]


def utc_now() -> datetime:
    return datetime.now(UTC)


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} no puede ser vacio")


def _require_non_empty_list(values: list[str], field_name: str) -> None:
    if not values:
        raise ValueError(f"{field_name} debe tener al menos un item")
    if any((not isinstance(value, str) or not value.strip()) for value in values):
        raise ValueError(f"{field_name} no puede contener items vacios")


class SignalNode(BaseModel):
    node_id: str = Field(...)
    tenant_id: str = Field(...)
    signal_code: str = Field(...)
    kind: SignalNodeKind = Field(...)
    severity: str = Field(...)
    evidence_refs: list[str] = Field(default_factory=list)
    source_finding_ids: list[str] = Field(default_factory=list)
    explanation: str = Field(...)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    period: str | None = Field(default=None)
    valid_from: datetime | None = Field(default=None)
    valid_until: datetime | None = Field(default=None)
    status: SmartGraphNodeStatus = Field(default="OBSERVED")
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def _validate_rules(self) -> "SignalNode":
        _require_non_empty(self.node_id, "node_id")
        _require_non_empty(self.tenant_id, "tenant_id")
        _require_non_empty(self.signal_code, "signal_code")
        _require_non_empty(self.severity, "severity")
        _require_non_empty(self.explanation, "explanation")
        _require_non_empty_list(self.evidence_refs, "evidence_refs")

        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValueError("valid_until no puede ser anterior a valid_from")

        if self.status == "REJECTED" and self.confidence is not None and self.confidence > 0.2:
            raise ValueError("confidence debe ser <= 0.2 cuando status == REJECTED")

        return self


class HypothesisNode(BaseModel):
    node_id: str = Field(...)
    tenant_id: str = Field(...)
    hypothesis_code: str = Field(...)
    description: str = Field(...)
    supporting_signal_node_ids: list[str] = Field(default_factory=list)
    contradicting_signal_node_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    ambiguity_score: float = Field(..., ge=0.0, le=1.0)
    requires_clarification: bool = Field(...)
    clarification_question: str | None = Field(default=None)
    status: HypothesisNodeStatus = Field(default="CANDIDATE")
    valid_from: datetime | None = Field(default=None)
    valid_until: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def _validate_rules(self) -> "HypothesisNode":
        _require_non_empty(self.node_id, "node_id")
        _require_non_empty(self.tenant_id, "tenant_id")
        _require_non_empty(self.hypothesis_code, "hypothesis_code")
        _require_non_empty(self.description, "description")
        _require_non_empty_list(self.supporting_signal_node_ids, "supporting_signal_node_ids")

        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValueError("valid_until no puede ser anterior a valid_from")

        if self.requires_clarification:
            _require_non_empty(self.clarification_question or "", "clarification_question")

        if self.status == "NEEDS_CLARIFICATION" and not self.requires_clarification:
            raise ValueError(
                "requires_clarification debe ser True cuando status == NEEDS_CLARIFICATION"
            )

        if self.status == "SUPPORTED" and self.ambiguity_score > 0.5:
            raise ValueError("ambiguity_score debe ser <= 0.5 cuando status == SUPPORTED")

        if self.status == "REJECTED" and self.confidence > 0.2:
            raise ValueError("confidence debe ser <= 0.2 cuando status == REJECTED")

        return self


class OwnerCriterionNode(BaseModel):
    node_id: str = Field(...)
    tenant_id: str = Field(...)
    criterion_code: str = Field(...)
    description: str = Field(...)
    captured_from: str = Field(...)
    related_hypothesis_node_ids: list[str] = Field(default_factory=list)
    related_signal_node_ids: list[str] = Field(default_factory=list)
    ambiguity_delta: float | None = Field(default=None, ge=-1.0, le=1.0)
    valid_from: datetime | None = Field(default=None)
    valid_until: datetime | None = Field(default=None)
    status: OwnerCriterionNodeStatus = Field(default="CAPTURED")
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def _validate_rules(self) -> "OwnerCriterionNode":
        _require_non_empty(self.node_id, "node_id")
        _require_non_empty(self.tenant_id, "tenant_id")
        _require_non_empty(self.criterion_code, "criterion_code")
        _require_non_empty(self.description, "description")
        _require_non_empty(self.captured_from, "captured_from")

        if not self.related_hypothesis_node_ids and not self.related_signal_node_ids:
            raise ValueError(
                "related_hypothesis_node_ids o related_signal_node_ids debe tener al menos un item"
            )

        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValueError("valid_until no puede ser anterior a valid_from")

        if self.status == "APPLIED" and self.ambiguity_delta is None:
            raise ValueError("ambiguity_delta es obligatorio cuando status == APPLIED")

        if self.status == "APPLIED" and self.ambiguity_delta is not None and self.ambiguity_delta >= 0:
            raise ValueError("ambiguity_delta debe reducir ambiguedad cuando status == APPLIED")

        return self


class OperationalPictureNode(BaseModel):
    node_id: str = Field(...)
    tenant_id: str = Field(...)
    picture_code: str = Field(...)
    title: str = Field(...)
    status: OperationalPictureNodeStatus = Field(default="DRAFT")
    signal_node_ids: list[str] = Field(default_factory=list)
    hypothesis_node_ids: list[str] = Field(default_factory=list)
    owner_criterion_node_ids: list[str] = Field(default_factory=list)
    principal_tension: str | None = Field(default=None)
    ambiguity_score: float = Field(..., ge=0.0, le=1.0)
    stability_score: float | None = Field(default=None, ge=0.0, le=1.0)
    valid_from: datetime | None = Field(default=None)
    valid_until: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def _validate_rules(self) -> "OperationalPictureNode":
        _require_non_empty(self.node_id, "node_id")
        _require_non_empty(self.tenant_id, "tenant_id")
        _require_non_empty(self.picture_code, "picture_code")
        _require_non_empty(self.title, "title")
        _require_non_empty_list(self.signal_node_ids, "signal_node_ids")
        _require_non_empty_list(self.hypothesis_node_ids, "hypothesis_node_ids")

        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValueError("valid_until no puede ser anterior a valid_from")

        if self.status == "STABILIZED":
            if not self.owner_criterion_node_ids:
                raise ValueError(
                    "owner_criterion_node_ids debe tener al menos un item cuando status == STABILIZED"
                )
            if not self.principal_tension or not self.principal_tension.strip():
                raise ValueError("principal_tension es obligatorio cuando status == STABILIZED")
            if self.stability_score is None:
                raise ValueError("stability_score es obligatorio cuando status == STABILIZED")
            if self.ambiguity_score > 0.4:
                raise ValueError("ambiguity_score debe ser <= 0.4 cuando status == STABILIZED")

        if self.status == "NEEDS_CLARIFICATION" and self.ambiguity_score < 0.5:
            raise ValueError("ambiguity_score debe ser >= 0.5 cuando status == NEEDS_CLARIFICATION")

        return self
