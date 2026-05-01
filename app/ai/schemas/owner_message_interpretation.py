from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OwnerMessageInterpretation(BaseModel):
    """Validated soft interpretation of an owner message.

    This is not a decision, diagnosis, finding, or persisted business fact.
    """

    model_config = ConfigDict(extra="forbid")

    intent: str | None = None
    entities: list[str] = Field(default_factory=list)
    variables: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    doubts: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
