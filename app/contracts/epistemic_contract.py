from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class UnknownSourceRequired(str, Enum):
    DOCUMENT = "DOCUMENT"
    HUMAN_INPUT = "HUMAN_INPUT"
    SYSTEM_COMPUTATION = "SYSTEM_COMPUTATION"


class EpistemicRegion(str, Enum):
    STATE_NULL = "STATE_NULL"
    STATE_SIGNAL = "STATE_SIGNAL"
    STATE_CASE_OPEN = "STATE_CASE_OPEN"
    STATE_EVIDENCE_PARTIAL = "STATE_EVIDENCE_PARTIAL"
    STATE_EVIDENCE_CONTRADICTORY = "STATE_EVIDENCE_CONTRADICTORY"
    STATE_READY_TO_DECIDE = "STATE_READY_TO_DECIDE"
    STATE_OWNER_AUTH_REQUIRED = "STATE_OWNER_AUTH_REQUIRED"
    STATE_EXECUTABLE = "STATE_EXECUTABLE"
    STATE_BLOCKED = "STATE_BLOCKED"
    STATE_CLOSED = "STATE_CLOSED"


class UnknownEntity(BaseModel):
    """Missing piece required to move an operational case to another state."""

    name: str = Field(..., description="Canonical observable name, e.g. ventas_por_producto.")
    description: str = Field(..., description="Why this observable is required.")
    source_required: UnknownSourceRequired = Field(
        ..., description="Where this missing piece must come from."
    )
    blocks_functions: list[str] = Field(
        default_factory=list,
        description="Math or operational functions blocked by this missing observable.",
    )
    accepted_formats: list[str] = Field(
        default_factory=list,
        description="Accepted formats for collecting this observable.",
    )

    @model_validator(mode="after")
    def _validate(self) -> "UnknownEntity":
        if not self.name.strip():
            raise ValueError("unknown name is required")
        if not self.description.strip():
            raise ValueError("unknown description is required")
        if any(not item.strip() for item in self.blocks_functions):
            raise ValueError("blocks_functions cannot contain empty strings")
        if any(not item.strip() for item in self.accepted_formats):
            raise ValueError("accepted_formats cannot contain empty strings")
        return self


class MathFunctionSpec(BaseModel):
    """Deterministic calculation contract: required inputs and produced output."""

    function_name: str = Field(..., description="Canonical function name, e.g. rotacion_stock.")
    required_inputs: list[str] = Field(..., min_length=1)
    output_entity: str = Field(..., description="Canonical output entity produced by the function.")
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = "LOW"
    reversible: bool = True

    @model_validator(mode="after")
    def _validate(self) -> "MathFunctionSpec":
        if not self.function_name.strip():
            raise ValueError("function_name is required")
        if not self.output_entity.strip():
            raise ValueError("output_entity is required")
        if any(not item.strip() for item in self.required_inputs):
            raise ValueError("required_inputs cannot contain empty strings")
        if len(set(self.required_inputs)) != len(self.required_inputs):
            raise ValueError("required_inputs cannot contain duplicates")
        return self


class EpistemicReadinessState(BaseModel):
    """State of the operational puzzle before any deterministic calculation runs."""

    cliente_id: str
    region: EpistemicRegion
    present_evidence_ids: list[str] = Field(default_factory=list)
    present_observables: list[str] = Field(default_factory=list)
    critical_unknowns: list[UnknownEntity] = Field(default_factory=list)
    blocked_functions: list[str] = Field(default_factory=list)
    enabled_functions: list[str] = Field(default_factory=list)
    allowed_transitions: list[str] = Field(default_factory=list)
    forbidden_transitions: list[str] = Field(default_factory=list)
    next_required_observable: str | None = None
    next_action_prompt: str | None = None
    collapse_reason: str

    @model_validator(mode="after")
    def _validate(self) -> "EpistemicReadinessState":
        if not self.cliente_id.strip():
            raise ValueError("cliente_id is required")
        if not self.collapse_reason.strip():
            raise ValueError("collapse_reason is required")
        for field_name in (
            "present_evidence_ids",
            "present_observables",
            "blocked_functions",
            "enabled_functions",
            "allowed_transitions",
            "forbidden_transitions",
        ):
            values = getattr(self, field_name)
            if any(not item.strip() for item in values):
                raise ValueError(f"{field_name} cannot contain empty strings")
        if self.next_required_observable is not None and not self.next_required_observable.strip():
            raise ValueError("next_required_observable cannot be empty")
        if self.next_action_prompt is not None and not self.next_action_prompt.strip():
            raise ValueError("next_action_prompt cannot be empty")
        if self.critical_unknowns and not self.next_required_observable:
            raise ValueError("next_required_observable is required when critical_unknowns exist")
        return self
