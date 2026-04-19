from app.core.reconciliation.models import ComparableRecord, DifferenceRecord

BLOCKING_FIELDS = {"cuit", "cuil", "sku", "entity_id"}


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
