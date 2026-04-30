from app.contracts.formula_contract import (
    FormulaInput,
    FormulaStatus,
    calculate_formula,
)


def test_margen_bruto_ok():
    result = calculate_formula(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["fact:ventas:1"]),
            FormulaInput(name="costos", value=600, source_refs=["fact:costos:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 0.4
    assert result.source_refs == ["fact:ventas:1", "fact:costos:1"]


def test_ganancia_bruta_ok():
    result = calculate_formula(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["fact:ventas:1"]),
            FormulaInput(name="costos", value=600, source_refs=["fact:costos:1"]),
        ],
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 400.0


def test_margen_bruto_blocked_by_zero_sales():
    result = calculate_formula(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=0, source_refs=["fact:ventas:zero"]),
            FormulaInput(name="costos", value=600, source_refs=["fact:costos:1"]),
        ],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "DIVISION_BY_ZERO: ventas"


def test_formula_missing_input_blocked():
    result = calculate_formula(
        "ganancia_bruta",
        [FormulaInput(name="ventas", value=1000, source_refs=["fact:ventas:1"])],
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.value is None
    assert result.blocking_reason == "MISSING_INPUTS: costos"
