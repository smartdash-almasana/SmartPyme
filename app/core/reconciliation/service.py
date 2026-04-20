from typing import Any

from app.core.reconciliation.models import (
    ComparableRecord,
    DifferenceRecord,
    QuantifiedDiscrepancy,
    ReconciledMatch,
    ReconciliationResult,
)

BLOCKING_FIELDS = {"cuit", "cuil", "sku", "entity_id"}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_present(value: str | int | float | bool | None) -> bool:
    return value is not None


def compare_records(record_a: ComparableRecord, record_b: ComparableRecord) -> list[DifferenceRecord]:
    if record_a.entity_id != record_b.entity_id:
        raise ValueError(
            "ENTITY_ID_MISMATCH: los records comparables deben tener el mismo entity_id."
        )

    if record_a.entity_type != record_b.entity_type:
        raise ValueError(
            "ENTITY_TYPE_MISMATCH: los records comparables deben tener el mismo entity_type."
        )

    field_names = sorted(set(record_a.fields.keys()) | set(record_b.fields.keys()))
    differences: list[DifferenceRecord] = []

    for field_name in field_names:
        value_a = record_a.fields.get(field_name)
        value_b = record_b.fields.get(field_name)

        if value_a == value_b:
            continue

        present_a = _is_present(value_a)
        present_b = _is_present(value_b)

        if not present_a and present_b:
            difference_type = "faltante_en_a"
        elif present_a and not present_b:
            difference_type = "faltante_en_b"
        else:
            difference_type = "valor_distinto"

        differences.append(
            DifferenceRecord(
                entity_id=record_a.entity_id,
                entity_type=record_a.entity_type,
                field_name=field_name,
                source_a=record_a.source,
                source_b=record_b.source,
                value_a=value_a,
                value_b=value_b,
                difference_type=difference_type,
                blocking=field_name in BLOCKING_FIELDS,
            )
        )

    return differences


def _validate_key_field(key_field: str) -> None:
    if not key_field or not key_field.strip():
        raise ValueError("KEY_FIELD_INVALIDO: key_field no puede ser vacio.")


def _index_records(
    source: list[dict[str, Any]], key_field: str, source_name: str
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in source:
        if key_field not in record:
            raise ValueError(
                f"KEY_FIELD_FALTANTE: falta '{key_field}' en un registro de {source_name}."
            )
        key_value = record[key_field]
        if key_value is None:
            raise ValueError(
                f"KEY_FIELD_NULO: '{key_field}' es nulo en un registro de {source_name}."
            )
        key = str(key_value)
        if key in indexed:
            raise ValueError(
                f"KEY_DUPLICADA: '{key}' duplicada en {source_name}. Ejecucion bloqueada."
            )
        indexed[key] = record
    return indexed


def reconcile_records(
    source_a: list[dict[str, Any]], source_b: list[dict[str, Any]], key_field: str
) -> ReconciliationResult:
    _validate_key_field(key_field)

    indexed_a = _index_records(source_a, key_field, "source_a")
    indexed_b = _index_records(source_b, key_field, "source_b")

    keys_a = set(indexed_a.keys())
    keys_b = set(indexed_b.keys())

    common_keys = sorted(keys_a & keys_b)
    missing_in_a_keys = sorted(keys_b - keys_a)
    missing_in_b_keys = sorted(keys_a - keys_b)

    matches: list[ReconciledMatch] = []
    mismatches: list[QuantifiedDiscrepancy] = []

    for key in common_keys:
        record_a = indexed_a[key]
        record_b = indexed_b[key]
        common_fields = sorted((set(record_a.keys()) & set(record_b.keys())) - {key_field})

        key_has_mismatch = False
        for field_name in common_fields:
            value_a = record_a[field_name]
            value_b = record_b[field_name]
            if value_a == value_b:
                continue

            key_has_mismatch = True
            if _is_number(value_a) and _is_number(value_b):
                delta = float(value_b) - float(value_a)
                detail = "mismatch_numerico"
            else:
                delta = None
                detail = "mismatch_no_numerico"

            mismatches.append(
                QuantifiedDiscrepancy(
                    key=key,
                    field_name=field_name,
                    value_a=value_a,
                    value_b=value_b,
                    delta=delta,
                    detail=detail,
                )
            )

        if not key_has_mismatch:
            matches.append(ReconciledMatch(key=key, record_a=record_a, record_b=record_b))

    missing_in_a = [indexed_b[key] for key in missing_in_a_keys]
    missing_in_b = [indexed_a[key] for key in missing_in_b_keys]

    return ReconciliationResult(
        matches=matches,
        mismatches=mismatches,
        missing_in_a=missing_in_a,
        missing_in_b=missing_in_b,
    )
