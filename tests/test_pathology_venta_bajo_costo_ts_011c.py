from app.contracts.formula_contract import FormulaInput
from app.contracts.pathology_contract import PathologyEvaluationInput, PathologyStatus
from app.services.formula_engine_service import FormulaEngineService
from app.services.pathology_engine_service import PathologyEngineService


def _ganancia_bruta(ventas: float, costos: float):
    return FormulaEngineService().calculate(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=ventas, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=costos, source_refs=["costos:1"]),
        ],
    )


def test_venta_bajo_costo_active_when_gross_profit_negative():
    result = PathologyEngineService().evaluate(
        "venta_bajo_costo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr1",
            formula_result=_ganancia_bruta(1000, 1200),
        ),
    )

    assert result.status == PathologyStatus.ACTIVE
    assert result.pathology_id == "venta_bajo_costo"
    assert result.severity is not None
    assert result.source_refs == ["ventas:1", "costos:1"]
    assert result.metadata["catalog"]["category"] == "pricing"


def test_venta_bajo_costo_not_detected_when_gross_profit_positive():
    result = PathologyEngineService().evaluate(
        "venta_bajo_costo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr2",
            formula_result=_ganancia_bruta(1000, 600),
        ),
    )

    assert result.status == PathologyStatus.NOT_DETECTED
    assert result.severity is None
    assert result.metadata["catalog"]["category"] == "pricing"


def test_venta_bajo_costo_pending_data_when_wrong_formula():
    formula_result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=1200),
        ],
    )

    result = PathologyEngineService().evaluate(
        "venta_bajo_costo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr3",
            formula_result=formula_result,
        ),
    )

    assert result.status == PathologyStatus.PENDING_DATA
    assert result.metadata["expected_formula_id"] == "ganancia_bruta"
