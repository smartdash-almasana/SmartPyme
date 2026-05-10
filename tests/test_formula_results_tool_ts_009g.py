from app.contracts.formula_contract import FormulaInput
from app.agents.formula_calculation_agent import FormulaCalculationAgent
from app.mcp.tools.formula_results_tool import (
    get_formula_result,
    get_formula_results,
    get_formula_status_for_owner,
    interpret_formula_result,
)


def test_formula_tool_reads_results(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    db = data_dir / "formula_results.db"
    monkeypatch.setenv("SMARTPYME_FORMULA_RESULTS_DB_PATH", str(db))
    monkeypatch.setenv("SMARTPYME_PATHOLOGIES_DB_PATH", str(data_dir / "pathologies.db"))
    monkeypatch.setenv("SMARTPYME_JOBS_DB_PATH", str(data_dir / "jobs.db"))
    monkeypatch.setenv("SMARTPYME_FINDINGS_DB_PATH", str(data_dir / "findings.db"))
    agent = FormulaCalculationAgent("pyme_A", db)
    agent.calculate_and_persist(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=600, source_refs=["costos:1"]),
        ],
        result_id="r1",
    )

    results = get_formula_results("pyme_A")

    assert len(results) == 1
    assert results[0]["formula_id"] == "ganancia_bruta"
    assert results[0]["value"] == 400.0


def test_formula_tool_hides_cross_client(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    db = data_dir / "formula_results.db"
    monkeypatch.setenv("SMARTPYME_FORMULA_RESULTS_DB_PATH", str(db))
    monkeypatch.setenv("SMARTPYME_PATHOLOGIES_DB_PATH", str(data_dir / "pathologies.db"))
    monkeypatch.setenv("SMARTPYME_JOBS_DB_PATH", str(data_dir / "jobs.db"))
    monkeypatch.setenv("SMARTPYME_FINDINGS_DB_PATH", str(data_dir / "findings.db"))
    agent = FormulaCalculationAgent("pyme_A", db)
    agent.calculate_and_persist(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=600),
        ],
        result_id="same-id",
    )

    assert get_formula_result("pyme_B", "same-id") is None


def test_formula_result_interpretation_ok():
    msg = interpret_formula_result({
        "formula_id": "ganancia_bruta",
        "status": "OK",
        "value": 400,
        "source_refs": ["ventas:1", "costos:1"],
    })

    assert "ganancia_bruta" in msg
    assert "400" in msg
    assert "Fuentes usadas: 2" in msg


def test_formula_status_for_owner(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    db = data_dir / "formula_results.db"
    monkeypatch.setenv("SMARTPYME_FORMULA_RESULTS_DB_PATH", str(db))
    monkeypatch.setenv("SMARTPYME_PATHOLOGIES_DB_PATH", str(data_dir / "pathologies.db"))
    monkeypatch.setenv("SMARTPYME_JOBS_DB_PATH", str(data_dir / "jobs.db"))
    monkeypatch.setenv("SMARTPYME_FINDINGS_DB_PATH", str(data_dir / "findings.db"))
    agent = FormulaCalculationAgent("pyme_A", db)
    agent.calculate_and_persist(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=0, source_refs=["ventas:zero"]),
            FormulaInput(name="costos", value=600, source_refs=["costos:1"]),
        ],
        result_id="blocked",
    )

    status = get_formula_status_for_owner("pyme_A")

    assert status["count"] == 1
    assert len(status["messages"]) == 1
    assert "No pude calcular margen_bruto" in status["messages"][0]
