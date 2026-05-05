"""
Tests — Contrato Pydantic Capa 03: OperationalCase v2
TS_030_001_CONTRATO_OPERATIONAL_CASE_V2

Valida el contrato definido en app/contracts/operational_case_v2_contract.py.

Cobertura:
  1. Construir OperationalCase con READY_FOR_INVESTIGATION.
  2. CLARIFICATION_REQUIRED requiere clarification_question.
  3. REJECTED_OUT_OF_SCOPE requiere rejection_reason.
  4. INSUFFICIENT_EVIDENCE requiere insufficiency_reason.
  5. status rechaza valores inválidos.
  6. OperationalCase no tiene atributos de DiagnosticReport ni FindingRecord.
  7. hypothesis vacía falla.
  8. Campos requeridos vacíos fallan.
  9. Trazabilidad: candidate_id y source_admission_case_id son opcionales.
  10. READY_FOR_INVESTIGATION no requiere ningún campo de razón.
"""

import pytest
from pydantic import ValidationError

from app.contracts.operational_case_v2_contract import OperationalCase


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ready_case(**overrides) -> OperationalCase:
    """Construye un OperationalCase mínimo válido con READY_FOR_INVESTIGATION."""
    defaults = dict(
        case_id="case_perales_001",
        cliente_id="cliente_perales",
        primary_pathology="inventario_no_confiable",
        hypothesis=(
            "Investigar si existe diferencia entre stock declarado y stock real "
            "para pantalones jean azul, período mayo 2026."
        ),
        status="READY_FOR_INVESTIGATION",
        next_step="Capa 04+: iniciar investigación sobre stock real vs stock declarado.",
    )
    defaults.update(overrides)
    return OperationalCase(**defaults)


# ---------------------------------------------------------------------------
# Test 1: Construir OperationalCase con READY_FOR_INVESTIGATION
# ---------------------------------------------------------------------------


def test_ready_for_investigation_valid():
    """OperationalCase con READY_FOR_INVESTIGATION debe construirse sin errores."""
    case = _ready_case()

    assert case.case_id == "case_perales_001"
    assert case.cliente_id == "cliente_perales"
    assert case.status == "READY_FOR_INVESTIGATION"
    assert case.primary_pathology == "inventario_no_confiable"
    assert case.hypothesis != ""
    assert case.next_step != ""
    assert case.clarification_question is None
    assert case.rejection_reason is None
    assert case.insufficiency_reason is None


def test_ready_for_investigation_does_not_require_reason_fields():
    """READY_FOR_INVESTIGATION no debe requerir ningún campo de razón."""
    case = OperationalCase(
        case_id="case_001",
        cliente_id="cli_001",
        primary_pathology="precio_desalineado",
        hypothesis="Investigar si existe desalineación entre costos y precios.",
        status="READY_FOR_INVESTIGATION",
        next_step="Iniciar investigación.",
        # Sin clarification_question, rejection_reason ni insufficiency_reason
    )
    assert case.status == "READY_FOR_INVESTIGATION"


# ---------------------------------------------------------------------------
# Test 2: CLARIFICATION_REQUIRED requiere clarification_question
# ---------------------------------------------------------------------------


def test_clarification_required_with_question_passes():
    """CLARIFICATION_REQUIRED con clarification_question debe pasar."""
    case = OperationalCase(
        case_id="case_002",
        cliente_id="cli_002",
        primary_pathology="precio_desalineado",
        hypothesis="Investigar si existe desalineación entre costos y precios.",
        status="CLARIFICATION_REQUIRED",
        clarification_question=(
            "¿Cuál es el precio de venta actual del Jean Azul talle 42? "
            "¿Es el mismo que figura en el Excel de Paulita ($5.500)?"
        ),
        next_step="Esperar respuesta del dueño antes de iniciar investigación.",
    )
    assert case.status == "CLARIFICATION_REQUIRED"
    assert case.clarification_question is not None


def test_clarification_required_without_question_fails():
    """CLARIFICATION_REQUIRED sin clarification_question debe fallar."""
    with pytest.raises(ValidationError, match="clarification_question"):
        OperationalCase(
            case_id="case_bad",
            cliente_id="cli_bad",
            primary_pathology="precio_desalineado",
            hypothesis="Investigar si existe desalineación.",
            status="CLARIFICATION_REQUIRED",
            next_step="Esperar.",
            # clarification_question ausente
        )


def test_clarification_required_with_empty_question_fails():
    """CLARIFICATION_REQUIRED con clarification_question vacía debe fallar."""
    with pytest.raises(ValidationError, match="clarification_question"):
        OperationalCase(
            case_id="case_bad",
            cliente_id="cli_bad",
            primary_pathology="precio_desalineado",
            hypothesis="Investigar si existe desalineación.",
            status="CLARIFICATION_REQUIRED",
            clarification_question="   ",
            next_step="Esperar.",
        )


# ---------------------------------------------------------------------------
# Test 3: REJECTED_OUT_OF_SCOPE requiere rejection_reason
# ---------------------------------------------------------------------------


def test_rejected_out_of_scope_with_reason_passes():
    """REJECTED_OUT_OF_SCOPE con rejection_reason debe pasar."""
    case = OperationalCase(
        case_id="case_003",
        cliente_id="cli_003",
        primary_pathology="patologia_fuera_dominio",
        hypothesis="Investigar si existe problema X.",
        status="REJECTED_OUT_OF_SCOPE",
        rejection_reason="La patología no corresponde al alcance operativo de SmartPyme.",
        next_step="Informar al dueño que el caso no puede investigarse.",
    )
    assert case.status == "REJECTED_OUT_OF_SCOPE"
    assert case.rejection_reason is not None


def test_rejected_out_of_scope_without_reason_fails():
    """REJECTED_OUT_OF_SCOPE sin rejection_reason debe fallar."""
    with pytest.raises(ValidationError, match="rejection_reason"):
        OperationalCase(
            case_id="case_bad",
            cliente_id="cli_bad",
            primary_pathology="patologia_fuera_dominio",
            hypothesis="Investigar si existe problema X.",
            status="REJECTED_OUT_OF_SCOPE",
            next_step="Informar.",
            # rejection_reason ausente
        )


def test_rejected_out_of_scope_with_empty_reason_fails():
    """REJECTED_OUT_OF_SCOPE con rejection_reason vacía debe fallar."""
    with pytest.raises(ValidationError, match="rejection_reason"):
        OperationalCase(
            case_id="case_bad",
            cliente_id="cli_bad",
            primary_pathology="patologia_fuera_dominio",
            hypothesis="Investigar si existe problema X.",
            status="REJECTED_OUT_OF_SCOPE",
            rejection_reason="",
            next_step="Informar.",
        )


# ---------------------------------------------------------------------------
# Test 4: INSUFFICIENT_EVIDENCE requiere insufficiency_reason
# ---------------------------------------------------------------------------


def test_insufficient_evidence_with_reason_passes():
    """INSUFFICIENT_EVIDENCE con insufficiency_reason debe pasar."""
    case = OperationalCase(
        case_id="case_004",
        cliente_id="cli_004",
        primary_pathology="inventario_no_confiable",
        hypothesis="Investigar si existe diferencia entre stock declarado y real.",
        status="INSUFFICIENT_EVIDENCE",
        insufficiency_reason=(
            "No hay variables disponibles con evidencia trazable. "
            "Las brechas críticas no tienen fuente conocida."
        ),
        next_step="Volver a Capa 1.5 para obtener nueva evidencia.",
    )
    assert case.status == "INSUFFICIENT_EVIDENCE"
    assert case.insufficiency_reason is not None


def test_insufficient_evidence_without_reason_fails():
    """INSUFFICIENT_EVIDENCE sin insufficiency_reason debe fallar."""
    with pytest.raises(ValidationError, match="insufficiency_reason"):
        OperationalCase(
            case_id="case_bad",
            cliente_id="cli_bad",
            primary_pathology="inventario_no_confiable",
            hypothesis="Investigar si existe diferencia.",
            status="INSUFFICIENT_EVIDENCE",
            next_step="Volver a Capa 1.5.",
            # insufficiency_reason ausente
        )


def test_insufficient_evidence_with_empty_reason_fails():
    """INSUFFICIENT_EVIDENCE con insufficiency_reason vacía debe fallar."""
    with pytest.raises(ValidationError, match="insufficiency_reason"):
        OperationalCase(
            case_id="case_bad",
            cliente_id="cli_bad",
            primary_pathology="inventario_no_confiable",
            hypothesis="Investigar si existe diferencia.",
            status="INSUFFICIENT_EVIDENCE",
            insufficiency_reason="   ",
            next_step="Volver a Capa 1.5.",
        )


# ---------------------------------------------------------------------------
# Test 5: status rechaza valores inválidos
# ---------------------------------------------------------------------------


def test_status_rejects_invalid_value():
    """status con valor fuera del Literal debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        OperationalCase(
            case_id="case_bad",
            cliente_id="cli_bad",
            primary_pathology="inventario_no_confiable",
            hypothesis="Investigar si existe diferencia.",
            status="DIAGNOSTIC_CONFIRMED",  # type: ignore[arg-type]
            next_step="Siguiente paso.",
        )


def test_status_accepts_all_four_valid_values():
    """Los 4 estados válidos deben ser aceptados."""
    # READY_FOR_INVESTIGATION
    c1 = _ready_case(status="READY_FOR_INVESTIGATION")
    assert c1.status == "READY_FOR_INVESTIGATION"

    # CLARIFICATION_REQUIRED
    c2 = OperationalCase(
        case_id="c2", cliente_id="cli", primary_pathology="p",
        hypothesis="Investigar si X.", status="CLARIFICATION_REQUIRED",
        clarification_question="¿Cuál es el precio actual?",
        next_step="Esperar.",
    )
    assert c2.status == "CLARIFICATION_REQUIRED"

    # INSUFFICIENT_EVIDENCE
    c3 = OperationalCase(
        case_id="c3", cliente_id="cli", primary_pathology="p",
        hypothesis="Investigar si X.", status="INSUFFICIENT_EVIDENCE",
        insufficiency_reason="Sin evidencia trazable.",
        next_step="Volver a Capa 1.5.",
    )
    assert c3.status == "INSUFFICIENT_EVIDENCE"

    # REJECTED_OUT_OF_SCOPE
    c4 = OperationalCase(
        case_id="c4", cliente_id="cli", primary_pathology="p",
        hypothesis="Investigar si X.", status="REJECTED_OUT_OF_SCOPE",
        rejection_reason="Fuera de alcance.",
        next_step="Informar al dueño.",
    )
    assert c4.status == "REJECTED_OUT_OF_SCOPE"


# ---------------------------------------------------------------------------
# Test 6: OperationalCase no tiene atributos de DiagnosticReport ni FindingRecord
# ---------------------------------------------------------------------------


def test_no_diagnostic_report_attributes():
    """OperationalCase no debe tener atributos de DiagnosticReport."""
    case = _ready_case()

    assert not hasattr(case, "diagnosis_status")
    assert not hasattr(case, "findings")
    assert not hasattr(case, "evidence_used")
    assert not hasattr(case, "reasoning_summary")
    assert not hasattr(case, "report_id")
    assert not hasattr(case, "quantified_impact")


def test_no_finding_record_attributes():
    """OperationalCase no debe tener atributos de FindingRecord."""
    case = _ready_case()

    assert not hasattr(case, "entity")
    assert not hasattr(case, "finding_type")
    assert not hasattr(case, "measured_difference")
    assert not hasattr(case, "compared_sources")
    assert not hasattr(case, "severity")
    assert not hasattr(case, "recommendation")


def test_no_action_proposal_attributes():
    """OperationalCase no debe tener atributos de ActionProposal."""
    case = _ready_case()

    assert not hasattr(case, "recommended_action")
    assert not hasattr(case, "rationale")
    assert not hasattr(case, "requires_owner_decision")
    assert not hasattr(case, "action_id")


# ---------------------------------------------------------------------------
# Test 7: hypothesis vacía falla
# ---------------------------------------------------------------------------


def test_hypothesis_empty_fails():
    """hypothesis vacía debe lanzar ValidationError."""
    with pytest.raises(ValidationError, match="vacía"):
        OperationalCase(
            case_id="case_bad",
            cliente_id="cli_bad",
            primary_pathology="inventario_no_confiable",
            hypothesis="",
            status="READY_FOR_INVESTIGATION",
            next_step="Siguiente paso.",
        )


def test_hypothesis_whitespace_fails():
    """hypothesis con solo espacios debe lanzar ValidationError."""
    with pytest.raises(ValidationError, match="vacía"):
        OperationalCase(
            case_id="case_bad",
            cliente_id="cli_bad",
            primary_pathology="inventario_no_confiable",
            hypothesis="   ",
            status="READY_FOR_INVESTIGATION",
            next_step="Siguiente paso.",
        )


# ---------------------------------------------------------------------------
# Test 8: Campos requeridos vacíos fallan
# ---------------------------------------------------------------------------


def test_case_id_empty_fails():
    """case_id vacío debe fallar."""
    with pytest.raises(ValidationError):
        _ready_case(case_id="")


def test_cliente_id_empty_fails():
    """cliente_id vacío debe fallar."""
    with pytest.raises(ValidationError):
        _ready_case(cliente_id="")


def test_next_step_empty_fails():
    """next_step vacío debe fallar."""
    with pytest.raises(ValidationError):
        _ready_case(next_step="")


# ---------------------------------------------------------------------------
# Test 9: Trazabilidad — candidate_id y source_admission_case_id son opcionales
# ---------------------------------------------------------------------------


def test_optional_traceability_fields_default_to_none():
    """candidate_id y source_admission_case_id deben ser None por defecto."""
    case = _ready_case()

    assert case.candidate_id is None
    assert case.source_admission_case_id is None
    assert case.source_normalized_package_id is None
    assert case.opened_at is None


def test_traceability_fields_can_be_set():
    """candidate_id y source_admission_case_id pueden establecerse."""
    case = _ready_case(
        candidate_id="cand_perales_001",
        source_admission_case_id="case_admission_001",
        source_normalized_package_id="pkg_perales_001",
    )

    assert case.candidate_id == "cand_perales_001"
    assert case.source_admission_case_id == "case_admission_001"
    assert case.source_normalized_package_id == "pkg_perales_001"
