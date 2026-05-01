import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.findings.service import build_findings
from app.core.reconciliation.models import DifferenceRecord


def _difference(
    *,
    field_name: str,
    difference_type: str,
    blocking: bool = False,
    value_a: str | int | float | bool | None = "A",
    value_b: str | int | float | bool | None = "B",
) -> DifferenceRecord:
    return DifferenceRecord(
        entity_id="ent-001",
        entity_type="proveedor",
        field_name=field_name,
        source_a="sap",
        source_b="afip",
        value_a=value_a,
        value_b=value_b,
        difference_type=difference_type,
        blocking=blocking,
    )


def test_blocking_difference_becomes_critica():
    differences = [_difference(field_name="cuit", difference_type="valor_distinto", blocking=True)]

    findings = build_findings(differences)

    assert len(findings) == 1
    assert findings[0].severity == "critica"
    assert findings[0].suggested_action == "Requiere validación humana antes de continuar."


def test_valor_distinto_becomes_alta():
    differences = [
        _difference(
            field_name="direccion",
            difference_type="valor_distinto",
            blocking=False,
        )
    ]

    findings = build_findings(differences)

    assert findings[0].severity == "alta"
    assert findings[0].suggested_action == "Comparar ambas fuentes y definir valor canónico."


def test_faltante_en_a_becomes_media_with_correct_action():
    differences = [
        _difference(
            field_name="telefono",
            difference_type="faltante_en_a",
            value_a=None,
            value_b="1234",
        )
    ]

    findings = build_findings(differences)

    assert findings[0].severity == "media"
    assert findings[0].suggested_action == (
        "Completar el dato faltante en la fuente A o validar ausencia."
    )


def test_faltante_en_b_becomes_media_with_correct_action():
    differences = [
        _difference(
            field_name="email",
            difference_type="faltante_en_b",
            value_a="a@b.com",
            value_b=None,
        )
    ]

    findings = build_findings(differences)

    assert findings[0].severity == "media"
    assert findings[0].suggested_action == (
        "Completar el dato faltante en la fuente B o validar ausencia."
    )


def test_title_is_correct_and_deterministic():
    differences = [
        _difference(field_name="cuit", difference_type="valor_distinto"),
        _difference(field_name="direccion", difference_type="faltante_en_a", value_a=None),
    ]

    findings = build_findings(differences)

    assert findings[0].title == "Diferencia en cuit"
    assert findings[1].title == "Falta dato en una fuente: direccion"


def test_finding_id_is_deterministic():
    differences = [_difference(field_name="cuit", difference_type="valor_distinto")]

    findings = build_findings(differences)

    assert findings[0].finding_id == "ent-001:cuit:valor_distinto"


def test_input_order_is_preserved():
    differences = [
        _difference(field_name="zeta", difference_type="valor_distinto"),
        _difference(field_name="alfa", difference_type="faltante_en_b"),
    ]

    findings = build_findings(differences)

    assert [finding.field_name for finding in findings] == ["zeta", "alfa"]


def test_empty_differences_returns_empty_list():
    findings = build_findings([])

    assert findings == []
