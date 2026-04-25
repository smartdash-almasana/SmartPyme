from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Entity:
    entity_id: str
    entity_type: str
    attributes: dict[str, Any] = field(default_factory=dict)
    linked_canonical_rows: list[str] = field(default_factory=list)
    validation_status: str = "pending_validation"
    errors: list[str] = field(default_factory=list)
