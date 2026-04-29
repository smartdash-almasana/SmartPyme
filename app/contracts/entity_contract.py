from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Entity:
    cliente_id: str
    entity_id: str
    entity_type: str
    attributes: dict[str, Any] = field(default_factory=dict)
    linked_canonical_rows: list[str] = field(default_factory=list)
    validation_status: str = "pending_validation"
    errors: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.cliente_id or not self.cliente_id.strip():
            raise ValueError("cliente_id is required")
