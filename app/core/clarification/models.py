from dataclasses import dataclass


@dataclass(frozen=True)
class ClarificationRequest:
    clarification_id: str
    entity_type: str
    value_a: str
    value_b: str
    reason: str
    blocking: bool


@dataclass(frozen=True)
class ClarificationRecord:
    clarification_id: str
    entity_type: str
    value_a: str
    value_b: str
    reason: str
    blocking: bool
    status: str
    resolution: str | None
