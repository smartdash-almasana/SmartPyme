from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation

SoftInterpretationStatus = Literal["ok", "empty", "failed"]
SoftInterpretationSource = Literal["local_adapter"]


class SoftInterpretationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_message: str
    interpretation: OwnerMessageInterpretation = Field(default_factory=OwnerMessageInterpretation)
    status: SoftInterpretationStatus
    source: SoftInterpretationSource = "local_adapter"
    errors: list[str] = Field(default_factory=list)

    @classmethod
    def ok(
        cls,
        *,
        raw_message: str,
        interpretation: OwnerMessageInterpretation,
    ) -> "SoftInterpretationResult":
        return cls(
            raw_message=raw_message,
            interpretation=interpretation,
            status="ok",
            errors=[],
        )

    @classmethod
    def empty(cls, *, raw_message: str) -> "SoftInterpretationResult":
        return cls(
            raw_message=raw_message,
            interpretation=OwnerMessageInterpretation(),
            status="empty",
            errors=[],
        )

    @classmethod
    def failed(
        cls,
        *,
        raw_message: str,
        errors: list[str] | None = None,
    ) -> "SoftInterpretationResult":
        return cls(
            raw_message=raw_message,
            interpretation=OwnerMessageInterpretation(),
            status="failed",
            errors=errors or [],
        )
