from dataclasses import dataclass


@dataclass(frozen=True)
class FindingRecord:
    finding_id: str
    entity_id: str
    entity_type: str
    field_name: str
    severity: str
    title: str
    detail: str
    suggested_action: str
    blocking: bool
