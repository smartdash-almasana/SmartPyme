from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")


def _require_non_empty_items(values: list[str], field_name: str) -> None:
    if any((not isinstance(item, str) or not item.strip()) for item in values):
        raise ValueError(f"{field_name} cannot contain empty strings")


class TensionKind(str, Enum):
    DOCUMENTAL = "documental"
    OPERACIONAL = "operacional"
    TEMPORAL = "temporal"
    FUENTE = "fuente"


class NodeStatus(str, Enum):
    CONFIRMADO = "CONFIRMADO"
    INFERIDO = "INFERIDO"
    PENDIENTE = "PENDIENTE"
    BLOQUEADO = "BLOQUEADO"
    DECISION_REQUERIDA = "DECISION_REQUERIDA"
    AMBIGUOUS = "AMBIGUOUS"
    AWAITING_CLARIFICATION = "AWAITING_CLARIFICATION"
    BLOCKED_BY_PARENT = "BLOCKED_BY_PARENT"


class NodeKind(str, Enum):
    FACT = "fact"
    SIGNAL = "signal"
    HYPOTHESIS = "hypothesis"
    HUMAN_INPUT = "human_input"
    OPERATIONAL_TRUTH = "operational_truth"


class TensionStatus(str, Enum):
    OK = "ok"
    ALERT = "alert"
    OPEN = "open"
    RESOLVED = "resolved"
    BLOCKING = "blocking"


class SourceOfTruth(BaseModel):
    evidence_ids: list[str] = Field(default_factory=list)
    formula_id: str | None = Field(default=None)
    human_input_id: str | None = Field(default=None)
    policy_id: str | None = Field(default=None)

    @model_validator(mode="after")
    def _validate(self) -> SourceOfTruth:
        _require_non_empty_items(self.evidence_ids, "evidence_ids")
        if self.formula_id is not None:
            _require_non_empty(self.formula_id, "formula_id")
        if self.human_input_id is not None:
            _require_non_empty(self.human_input_id, "human_input_id")
        if self.policy_id is not None:
            _require_non_empty(self.policy_id, "policy_id")
        return self


class Tension(BaseModel):
    kind: TensionKind
    score: float = Field(..., ge=0.0)
    threshold: float = Field(..., ge=0.0)
    status: TensionStatus = Field(default=TensionStatus.OPEN)
    explanation: str | None = Field(default=None)

    @model_validator(mode="after")
    def _validate(self) -> Tension:
        if self.explanation is not None:
            _require_non_empty(self.explanation, "explanation")
        return self


class ValidityWindow(BaseModel):
    valid_from: datetime
    valid_until: datetime

    @model_validator(mode="after")
    def _validate(self) -> ValidityWindow:
        if self.valid_until <= self.valid_from:
            raise ValueError("valid_until must be later than valid_from")
        return self


class BaseGraphNode(BaseModel):
    cliente_id: str
    node_id: str
    kind: NodeKind
    status: NodeStatus = Field(default=NodeStatus.PENDIENTE)
    certainty: float = Field(..., ge=0.0, le=1.0)
    tensions: list[Tension] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    source_of_truth: SourceOfTruth = Field(default_factory=SourceOfTruth)

    @model_validator(mode="after")
    def _validate(self) -> BaseGraphNode:
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.node_id, "node_id")
        _require_non_empty_items(self.dependencies, "dependencies")
        return self


class FactNode(BaseGraphNode):
    kind: NodeKind = Field(default=NodeKind.FACT)

    @model_validator(mode="after")
    def _validate_fact(self) -> FactNode:
        has_evidence = bool(self.source_of_truth.evidence_ids)
        has_formula = bool(self.source_of_truth.formula_id)
        has_human_input = bool(self.source_of_truth.human_input_id)

        if not has_evidence and not has_formula:
            raise ValueError("FactNode requires evidence_ids or formula_id")

        if has_human_input and not has_evidence and not has_formula:
            raise ValueError("FactNode cannot depend only on human_input_id")

        return self


class SignalNode(BaseGraphNode):
    kind: NodeKind = Field(default=NodeKind.SIGNAL)


class HypothesisNode(BaseGraphNode):
    kind: NodeKind = Field(default=NodeKind.HYPOTHESIS)
    supporting_node_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_hypothesis(self) -> HypothesisNode:
        _require_non_empty_items(self.supporting_node_ids, "supporting_node_ids")
        return self


class HumanInputNode(BaseGraphNode):
    kind: NodeKind = Field(default=NodeKind.HUMAN_INPUT)
    input_text: str

    @model_validator(mode="after")
    def _validate_human_input(self) -> HumanInputNode:
        _require_non_empty(self.input_text, "input_text")
        return self


class OperationalTruthNode(BaseGraphNode):
    kind: NodeKind = Field(default=NodeKind.OPERATIONAL_TRUTH)
    validity_window: ValidityWindow
    human_input_id: str | None = Field(default=None)
    policy_id: str | None = Field(default=None)

    @model_validator(mode="after")
    def _validate_operational_truth(self) -> OperationalTruthNode:
        if self.human_input_id is not None:
            _require_non_empty(self.human_input_id, "human_input_id")
        if self.policy_id is not None:
            _require_non_empty(self.policy_id, "policy_id")
        if not self.human_input_id and not self.policy_id:
            raise ValueError("OperationalTruthNode requires human_input_id or policy_id")
        return self


class TruthConflict(BaseModel):
    cliente_id: str
    fact_node_id: str
    operational_truth_node_id: str
    conflict_kind: str
    explanation: str
    status: TensionStatus = Field(default=TensionStatus.BLOCKING)

    @model_validator(mode="after")
    def _validate(self) -> TruthConflict:
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.fact_node_id, "fact_node_id")
        _require_non_empty(self.operational_truth_node_id, "operational_truth_node_id")
        _require_non_empty(self.conflict_kind, "conflict_kind")
        _require_non_empty(self.explanation, "explanation")
        return self
