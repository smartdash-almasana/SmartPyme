from app.contracts.formula_contract import FormulaInput, FormulaStatus
from app.factory.agents.formula_calculation_agent import FormulaCalculationAgent
from app.repositories.formula_result_repository import FormulaResultRepository


def test_agent_calculates_and_persists(tmp_path):
    db = tmp_path / "formula_results.db"
    agent = FormulaCalculationAgent("pyme_A", db)

    result = agent.calculate_and_persist(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=700, source_refs=["costos:1"]),
        ],
        result_id="calc1",
    )

    assert result.status == FormulaStatus.OK
    assert result.value == 300.0
    assert result.metadata["result_id"] == "calc1"

    repo = FormulaResultRepository("pyme_A", db)
    persisted = repo.get("calc1")

    assert persisted is not None
    assert persisted.value == 300.0
    assert persisted.source_refs == ["ventas:1", "costos:1"]


def test_agent_persists_blocked_result(tmp_path):
    db = tmp_path / "formula_results.db"
    agent = FormulaCalculationAgent("pyme_A", db)

    result = agent.calculate_and_persist(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=0, source_refs=["ventas:zero"]),
            FormulaInput(name="costos", value=700, source_refs=["costos:1"]),
        ],
        result_id="calc_blocked",
    )

    assert result.status == FormulaStatus.BLOCKED
    assert result.blocking_reason == "DIVISION_BY_ZERO: ventas"

    repo = FormulaResultRepository("pyme_A", db)
    persisted = repo.get("calc_blocked")

    assert persisted is not None
    assert persisted.status == FormulaStatus.BLOCKED
    assert persisted.blocking_reason == "DIVISION_BY_ZERO: ventas"


def test_agent_result_isolation(tmp_path):
    db = tmp_path / "formula_results.db"
    agent_a = FormulaCalculationAgent("pyme_A", db)

    agent_a.calculate_and_persist(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=700),
        ],
        result_id="same-id",
    )

    repo_b = FormulaResultRepository("pyme_B", db)
    assert repo_b.get("same-id") is None
