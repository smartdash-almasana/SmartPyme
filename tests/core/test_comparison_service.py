import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.entity_contract import Entity
from app.services.comparison_service import ComparisonService


def _entity(
    entity_id: str,
    *,
    entity_type: str = "product",
    validation_status: str = "validated",
    attributes: dict | None = None,
) -> Entity:
    return Entity(
        entity_id=entity_id,
        entity_type=entity_type,
        validation_status=validation_status,
        attributes=attributes or {},
    )


def test_compare_entities_detects_difference():
    service = ComparisonService()
    entities = [
        _entity("p1", attributes={"price": 100}),
        _entity("p1", attributes={"price": 110}),
    ]

    results = service.compare_entities(entities)

    assert len(results) == 1
    result = results[0]
    assert result.entity_id_a == "p1"
    assert result.attribute == "price"
    assert result.value_a == 100
    assert result.value_b == 110
    assert result.difference == 10.0
    assert result.difference_pct == 10.0


def test_compare_entities_ignores_unvalidated():
    service = ComparisonService()
    entities = [
        _entity("p1", validation_status="pending_validation", attributes={"price": 100}),
        _entity("p1", attributes={"price": 110}),
    ]

    results = service.compare_entities(entities)

    assert len(results) == 0

def test_compare_entities_no_difference():
    service = ComparisonService()
    entities = [
        _entity("p1", attributes={"price": 100}),
        _entity("p1", attributes={"price": 100}),
    ]

    results = service.compare_entities(entities)

    assert len(results) == 0
