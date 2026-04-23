from dataclasses import dataclass
from typing import Literal, TypeAlias

ClarificationStatus: TypeAlias = Literal["pending", "resolved"]


@dataclass(frozen=True, slots=True)
class ClarificationRequest:
    clarification_id: str
    entity_type: str
    value_a: str
    value_b: str
    reason: str
    blocking: bool


@dataclass(frozen=True, slots=True)
class ClarificationRecord(ClarificationRequest):
    status: ClarificationStatus = "pending"
    resolution: str | None = None
