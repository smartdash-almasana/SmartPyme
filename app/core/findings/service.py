from app.core.findings.models import FindingRecord
from app.core.reconciliation.models import DifferenceRecord


def _build_finding_id(difference: DifferenceRecord) -> str:
    return f"{difference.entity_id}:{difference.field_name}:{difference.difference_type}"


def _resolve_severity(difference: DifferenceRecord) -> str:
    if difference.blocking is True:
        return "critica"
    if difference.difference_type == "valor_distinto":
        return "alta"
    if difference.difference_type in {"faltante_en_a", "faltante_en_b"}:
        return "media"
    raise ValueError(
        f"DIFFERENCE_TYPE_INVALIDO: difference_type no soportado: {difference.difference_type}"
    )


def _build_title(difference: DifferenceRecord) -> str:
    if difference.difference_type == "valor_distinto":
        return f"Diferencia en {difference.field_name}"
    if difference.difference_type in {"faltante_en_a", "faltante_en_b"}:
        return f"Falta dato en una fuente: {difference.field_name}"
    raise ValueError(
        f"DIFFERENCE_TYPE_INVALIDO: difference_type no soportado: {difference.difference_type}"
    )


def _build_suggested_action(difference: DifferenceRecord) -> str:
    if difference.blocking is True:
        return "Requiere validación humana antes de continuar."
    if difference.difference_type == "valor_distinto":
        return "Comparar ambas fuentes y definir valor canónico."
    if difference.difference_type == "faltante_en_a":
        return "Completar el dato faltante en la fuente A o validar ausencia."
    if difference.difference_type == "faltante_en_b":
        return "Completar el dato faltante en la fuente B o validar ausencia."
    raise ValueError(
        f"DIFFERENCE_TYPE_INVALIDO: difference_type no soportado: {difference.difference_type}"
    )


def _build_detail(difference: DifferenceRecord) -> str:
    entity_segment = f"Entidad {difference.entity_type} ({difference.entity_id})"
    field_segment = f"campo '{difference.field_name}'"
    source_segment = (
        f"comparado entre source_a='{difference.source_a}' "
        f"y source_b='{difference.source_b}'"
    )
    value_segment = f"con value_a={difference.value_a!r}, value_b={difference.value_b!r}"
    difference_segment = f"y difference_type='{difference.difference_type}'."
    return (
        f"{entity_segment}: {field_segment} {source_segment}, "
        f"{value_segment} {difference_segment}"
    )


def build_findings(differences: list[DifferenceRecord]) -> list[FindingRecord]:
    findings: list[FindingRecord] = []

    for difference in differences:
        finding = FindingRecord(
            finding_id=_build_finding_id(difference),
            entity_id=difference.entity_id,
            entity_type=difference.entity_type,
            field_name=difference.field_name,
            severity=_resolve_severity(difference),
            title=_build_title(difference),
            detail=_build_detail(difference),
            suggested_action=_build_suggested_action(difference),
            blocking=difference.blocking,
        )
        findings.append(finding)

    return findings
