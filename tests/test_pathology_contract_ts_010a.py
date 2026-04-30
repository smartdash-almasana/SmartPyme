from app.contracts.formula_contract import FormulaInput, FormulaStatus
from app.contracts.pathology_contract import (
    PathologyEvaluationInput,
    PathologySeverity,
    PathologyStatus,
    evaluate_pathology,
)
from app.services.formula_engine_service import FormulaEngineService


def test_margen_bruto_negativo_active():
    formula_result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=1200, source_refs=["costos:1"]),
        ],
    )

    finding = evaluate_pathology(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr1",
            formula_result=formula_result,
        ),
    )

    assert finding.cliente_id == "pyme_A"
    assert finding.status == PathologyStatus.ACTIVE
    assert finding.severity == PathologySeverity.HIGH
    assert finding.suggested_action is not None
    assert finding.source_refs == ["ventas:1", "costos:1"]


def test_margen_bruto_positivo_not_detected():
    formula_result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=600),
        ],
    )

    finding = evaluate_pathology(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr2",
            formula_result=formula_result,
        ),
    )

    assert finding.status == PathologyStatus.NOT_DETECTED
    assert finding.severity is None


def test_blocked_formula_returns_pending_data():
    formula_result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=0),
            FormulaInput(name="costos", value=600),
        ],
    )

    assert formula_result.status == FormulaStatus.BLOCKED

    finding = evaluate_pathology(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr3",
            formula_result=formula_result,
        ),
    )

    assert finding.status == PathologyStatus.PENDING_DATA
    assert finding.metadata["blocking_reason"] == "DIVISION_BY_ZERO: ventas"


def test_wrong_formula_returns_pending_data():
    formula_result = FormulaEngineService().calculate(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=600),
        ],
    )

    finding = evaluate_pathology(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr4",
            formula_result=formula_result,
        ),
    )

    assert finding.status == PathologyStatus.PENDING_DATA
    assert finding.metadata["expected_formula_id"] == "margen_bruto"
