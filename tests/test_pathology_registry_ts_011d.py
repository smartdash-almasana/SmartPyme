from app.contracts.formula_contract import FormulaInput
from app.contracts.pathology_contract import PathologyEvaluationInput, PathologyStatus
from app.services.formula_engine_service import FormulaEngineService
from app.services.pathology_engine_service import PathologyEngineService
from app.services.pathology_evaluators import EVALUATOR_REGISTRY, get_pathology_evaluator


def _formula_result(formula_id: str, ventas: float, costos: float):
    return FormulaEngineService().calculate(
        formula_id,
        [
            FormulaInput(name="ventas", value=ventas, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=costos, source_refs=["costos:1"]),
        ],
    )


def test_registry_contains_current_evaluators():
    assert "margen_bruto_negativo" in EVALUATOR_REGISTRY
    assert "venta_bajo_costo" in EVALUATOR_REGISTRY
    assert get_pathology_evaluator("margen_bruto_negativo") is not None
    assert get_pathology_evaluator("venta_bajo_costo") is not None


def test_engine_uses_registry_for_margen_bruto_negativo():
    result = PathologyEngineService().evaluate(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr1",
            formula_result=_formula_result("margen_bruto", 1000, 1200),
        ),
    )

    assert result.status == PathologyStatus.ACTIVE
    assert result.pathology_id == "margen_bruto_negativo"


def test_engine_uses_registry_for_venta_bajo_costo():
    result = PathologyEngineService().evaluate(
        "venta_bajo_costo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr2",
            formula_result=_formula_result("ganancia_bruta", 1000, 1200),
        ),
    )

    assert result.status == PathologyStatus.ACTIVE
    assert result.pathology_id == "venta_bajo_costo"


def test_catalog_pathology_without_registry_evaluator_is_pending_data():
    result = PathologyEngineService().evaluate(
        "falla_precision_int64",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr3",
            formula_result=_formula_result("integridad_identificador", 1000, 600),
        ),
    )

    assert result.status == PathologyStatus.PENDING_DATA
    assert result.metadata["blocking_reason"] == "PATHOLOGY_NOT_IMPLEMENTED"
