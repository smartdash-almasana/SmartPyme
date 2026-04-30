from app.contracts.formula_contract import FormulaInput
from app.contracts.pathology_contract import PathologyEvaluationInput, PathologyStatus
from app.services.formula_engine_service import FormulaEngineService
from app.services.pathology_engine_service import PathologyEngineService


def _formula_result(formula_id: str, ventas: float, costos: float):
    return FormulaEngineService().calculate(
        formula_id,
        [
            FormulaInput(name="ventas", value=ventas, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=costos, source_refs=["costos:1"]),
        ],
    )


def test_engine_uses_catalog_for_baseline_pathology():
    result = PathologyEngineService().evaluate(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr1",
            formula_result=_formula_result("margen_bruto", 1000, 1200),
        ),
    )

    assert result.status == PathologyStatus.ACTIVE
    assert result.metadata["catalog"]["category"] == "rentabilidad"


def test_engine_keeps_margen_bruto_negativo_not_detected():
    result = PathologyEngineService().evaluate(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr2",
            formula_result=_formula_result("margen_bruto", 1000, 600),
        ),
    )

    assert result.status == PathologyStatus.NOT_DETECTED
    assert result.metadata["catalog"]["category"] == "rentabilidad"


def test_catalog_pathology_without_evaluator_returns_pending_data():
    result = PathologyEngineService().evaluate(
        "venta_bajo_costo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr3",
            formula_result=_formula_result("ganancia_bruta", 1000, 1200),
        ),
    )

    assert result.status == PathologyStatus.PENDING_DATA
    assert result.metadata["blocking_reason"] == "PATHOLOGY_NOT_IMPLEMENTED"
    assert result.metadata["catalog"]["category"] == "pricing"


def test_unknown_pathology_still_pending_data():
    result = PathologyEngineService().evaluate(
        "unknown_pathology",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr4",
            formula_result=_formula_result("ganancia_bruta", 1000, 600),
        ),
    )

    assert result.status == PathologyStatus.PENDING_DATA
    assert result.metadata["blocking_reason"] == "PATHOLOGY_NOT_SUPPORTED"
