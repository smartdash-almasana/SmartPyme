from app.contracts.formula_contract import FormulaInput
from app.contracts.pathology_contract import (
    PathologyEvaluationInput,
    PathologyStatus,
    evaluate_pathology,
)
from app.services.formula_engine_service import FormulaEngineService
from app.services.pathology_engine_service import PathologyEngineService


def _margin_result(ventas: float, costos: float):
    return FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=ventas, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=costos, source_refs=["costos:1"]),
        ],
    )


def test_engine_detects_negative_margin():
    result = PathologyEngineService().evaluate(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr1",
            formula_result=_margin_result(1000, 1200),
        ),
    )

    assert result.status == PathologyStatus.ACTIVE
    assert result.cliente_id == "pyme_A"
    assert result.source_refs == ["ventas:1", "costos:1"]


def test_engine_not_detected_for_positive_margin():
    result = PathologyEngineService().evaluate(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr2",
            formula_result=_margin_result(1000, 600),
        ),
    )

    assert result.status == PathologyStatus.NOT_DETECTED


def test_engine_wrapper_compatibility():
    result = evaluate_pathology(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr3",
            formula_result=_margin_result(1000, 1200),
        ),
    )

    assert result.status == PathologyStatus.ACTIVE


def test_engine_unknown_pathology_pending_data():
    result = PathologyEngineService().evaluate(
        "unknown",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr4",
            formula_result=_margin_result(1000, 600),
        ),
    )

    assert result.status == PathologyStatus.PENDING_DATA
    assert result.metadata["blocking_reason"] == "PATHOLOGY_NOT_SUPPORTED"
