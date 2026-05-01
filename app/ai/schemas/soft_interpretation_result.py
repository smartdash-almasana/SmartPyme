from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation

SoftInterpretationStatus = Literal["ok", "empty", "failed"]
SoftInterpretationSource = Literal["local_adapter"]


class SoftInterpretationResult(BaseModel):
    """Stable result contract for soft owner-message interpretation.

    This contract is provisional input for future consumers.
    It is not a business decision, finding, persisted fact, or confirmed context.
    """

    model_config = ConfigDict(extra="forbid")

    raw_message: str
    interpretation: OwnerMessageInterpretation = Field(
        default_factory=OwnerMessageInterpretation
    )
    status: SoftInterpretationStatus
    source: SoftInterpretationSource = "local_adapter"
    errors: list[str] = Field(default_factory=list)

    @field_validator("raw_message")
    @classmethod
    def _raw_message_must_be_string(cls, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("raw_message must be a string")
        return value

    @classmethod
    def ok(
        cls,
        *,
        raw_message: str,
        interpretation: OwnerMessageInterpretation,
        source: SoftInterpretationSource = "local_adapter",
    ) -> "SoftInterpretationResult":
        return cls(
            raw_message=raw_message,
            interpretation=interpretation,
            status="ok",
            source=source,
            errors=[],
        )

    @classmethod
    def empty(
        cls,
        *,
        raw_message: str,
        source: SoftInterpretationSource = "local_adapter",
    ) -> "SoftInterpretationResult":
        return cls(
            raw_message=raw_message,
            interpretation=OwnerMessageInterpretation(),
            status="empty",
            source=source,
            errors=[],
        )

    @classmethod
    def failed(
        cls,
        *,
        raw_message: str,
        errors: list[str] | None = None,
        source: SoftInterpretationSource = "local_adapter",
    ) -> "SoftInterpretationResult":
        return cls(
            raw_message=raw_message,
            interpretation=OwnerMessageInterpretation(),
            status="failed",
            source=source,
            errors=errors or [],
        )
