from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ClarificationStatus = Literal["pending", "answered"]


@dataclass(frozen=True, slots=True)
class Clarification:
    clarification_id: str
    job_id: str | None
    question: str
    reason: str
    status: ClarificationStatus = "pending"
    blocking: bool = True
    answer: str | None = None
    traceable_origin: dict[str, Any] = field(default_factory=dict)
