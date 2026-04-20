from dataclasses import dataclass, field
from typing import Any

FieldValue = str | int | float | bool | None


@dataclass(frozen=True)
class ComparableRecord:
    entity_id: str
    entity_type: str
    source: str
    fields: dict[str, FieldValue] = field(default_factory=dict)


@dataclass(frozen=True)
class DifferenceRecord:
    entity_id: str
    entity_type: str
    field_name: str
    source_a: str
    source_b: str
    value_a: FieldValue
    value_b: FieldValue
    difference_type: str
    blocking: bool


@dataclass(frozen=True)
class ReconciledMatch:
    key: str
    record_a: dict[str, Any]
    record_b: dict[str, Any]


@dataclass(frozen=True)
class QuantifiedDiscrepancy:
    key: str
    field_name: str
    value_a: Any
    value_b: Any
    delta: float | None
    detail: str


@dataclass(frozen=True)
class ReconciliationResult:
    matches: list[ReconciledMatch]
    mismatches: list[QuantifiedDiscrepancy]
    missing_in_a: list[dict[str, Any]]
    missing_in_b: list[dict[str, Any]]
