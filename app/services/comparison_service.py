from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from itertools import combinations

from app.contracts.entity_contract import Entity

@dataclass(frozen=True, slots=True)
class ComparisonResult:
    entity_id_a: str
    entity_id_b: str
    entity_type: str
    attribute: str
    value_a: Any
    value_b: Any
    difference: float
    difference_pct: float

class ComparisonService:
    def compare_entities(self, entities: list[Entity]) -> list[ComparisonResult]:
        results = []
        for entity_a, entity_b in combinations(entities, 2):
            if entity_a.entity_type != entity_b.entity_type:
                continue

            if entity_a.validation_status != "validated" or entity_b.validation_status != "validated":
                continue

            for attr, value_a in entity_a.attributes.items():
                if attr in entity_b.attributes:
                    value_b = entity_b.attributes[attr]
                    if isinstance(value_a, (int, float)) and isinstance(value_b, (int, float)):
                        if value_a != value_b:
                            diff = float(value_b - value_a)
                            diff_pct = (diff / value_a) * 100 if value_a != 0 else 0
                            results.append(
                                ComparisonResult(
                                    entity_id_a=entity_a.entity_id,
                                    entity_id_b=entity_b.entity_id,
                                    entity_type=entity_a.entity_type,
                                    attribute=attr,
                                    value_a=value_a,
                                    value_b=value_b,
                                    difference=diff,
                                    difference_pct=diff_pct,
                                )
                            )
        return results
