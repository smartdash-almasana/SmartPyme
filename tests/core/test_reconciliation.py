import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.reconciliation.models import ComparableRecord
from app.core.reconciliation.service import compare_records


def _record(source: str, fields: dict[str, str | int | float | bool | None]) -> ComparableRecord:
    return ComparableRecord(
        entity_id="ent-001",
        entity_type="proveedor",
        source=source,
        fields=fields,
    )


def test_identical_records_return_empty_list():
    record_a = _record("sap", {"nombre": "ACME", "activo": True, "cuit": "20-11111111-1"})
    record_b = _record("afip", {"nombre": "ACME", "activo": True, "cuit": "20-11111111-1"})

    result = compare_records(record_a, record_b)

    assert result == []


def test_different_simple_value_returns_one_valor_distinto():
    record_a = _record("sap", {"nombre": "ACME"})
    record_b = _record("afip", {"nombre": "ACME SRL"})

    result = compare_records(record_a, record_b)

    assert len(result) == 1
    assert result[0].field_name == "nombre"
    assert result[0].difference_type == "valor_distinto"
    assert result[0].blocking is False


def test_missing_field_in_a_returns_faltante_en_a():
    record_a = _record("sap", {})
    record_b = _record("afip", {"direccion": "Calle 123"})

    result = compare_records(record_a, record_b)

    assert len(result) == 1
    assert result[0].field_name == "direccion"
    assert result[0].difference_type == "faltante_en_a"


def test_missing_field_in_b_returns_faltante_en_b():
    record_a = _record("sap", {"telefono": "1234"})
    record_b = _record("afip", {})

    result = compare_records(record_a, record_b)

    assert len(result) == 1
    assert result[0].field_name == "telefono"
    assert result[0].difference_type == "faltante_en_b"


def test_blocking_true_for_cuit_difference():
    record_a = _record("sap", {"cuit": "20-11111111-1"})
    record_b = _record("afip", {"cuit": "27-22222222-2"})

    result = compare_records(record_a, record_b)

    assert len(result) == 1
    assert result[0].field_name == "cuit"
    assert result[0].difference_type == "valor_distinto"
    assert result[0].blocking is True


def test_entity_id_mismatch_raises_explicit_error():
    record_a = ComparableRecord(
        entity_id="ent-001",
        entity_type="proveedor",
        source="sap",
        fields={"nombre": "ACME"},
    )
    record_b = ComparableRecord(
        entity_id="ent-999",
        entity_type="proveedor",
        source="afip",
        fields={"nombre": "ACME"},
    )

    with pytest.raises(ValueError, match="ENTITY_ID_MISMATCH"):
        compare_records(record_a, record_b)


def test_entity_type_mismatch_raises_explicit_error():
    record_a = ComparableRecord(
        entity_id="ent-001",
        entity_type="proveedor",
        source="sap",
        fields={"nombre": "ACME"},
    )
    record_b = ComparableRecord(
        entity_id="ent-001",
        entity_type="cliente",
        source="afip",
        fields={"nombre": "ACME"},
    )

    with pytest.raises(ValueError, match="ENTITY_TYPE_MISMATCH"):
        compare_records(record_a, record_b)


def test_output_ordering_is_deterministic_by_field_name():
    record_a = _record("sap", {"zeta": "A", "alfa": "A", "beta": "A"})
    record_b = _record("afip", {"zeta": "B", "alfa": "B", "beta": "B"})

    result = compare_records(record_a, record_b)

    assert [difference.field_name for difference in result] == ["alfa", "beta", "zeta"]
