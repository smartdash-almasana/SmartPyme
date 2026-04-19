from dataclasses import dataclass, field

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
