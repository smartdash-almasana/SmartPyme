from app.contracts.formula_contract import FormulaInput, FormulaStatus, calculate_formula
from app.services.formula_engine_service import FormulaEngineService


def test_engine_calculates_margen_bruto():
    result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=750, source_refs=["costos:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 0.25


def test_engine_calculates_ganancia_bruta():
    result = FormulaEngineService().calculate(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=750),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 250.0


def test_engine_blocks_division_by_zero():
    result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=0),
            FormulaInput(name="costos", value=750),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "DIVISION_BY_ZERO: ventas"


def test_contract_compatibility_wrapper():
    result = calculate_formula(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=750),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 250.0
