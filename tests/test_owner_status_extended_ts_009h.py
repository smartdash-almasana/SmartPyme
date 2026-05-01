from app.contracts.formula_contract import FormulaInput
from app.contracts.job_contract import Job
from app.agents.formula_calculation_agent import FormulaCalculationAgent
from app.mcp.tools.owner_status_tool import get_owner_status
from app.repositories.job_repository import JobRepository


def test_owner_status_includes_formula_results(tmp_path):
    jobs_db = tmp_path / "jobs.db"
    formula_db = tmp_path / "formula_results.db"

    JobRepository("pyme_A", jobs_db).create(Job(job_id="j1", cliente_id="pyme_A", job_type="TEST"))
    FormulaCalculationAgent("pyme_A", formula_db).calculate_and_persist(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=600, source_refs=["costos:1"]),
        ],
        result_id="r1",
    )

    import app.mcp.tools.formula_results_tool as formula_tool
    import app.mcp.tools.jobs_read_tool as jobs_tool

    jobs_tool.Path = lambda p: jobs_db if "jobs" in p else tmp_path / "findings.db"
    formula_tool.Path = lambda p: formula_db

    status = get_owner_status("pyme_A")

    assert status["jobs_count"] == 1
    assert status["formula_results_count"] == 1
    assert len(status["formula_results"]) == 1
    assert any("ganancia_bruta" in msg for msg in status["messages"])


def test_owner_status_formula_results_are_isolated(tmp_path):
    formula_db = tmp_path / "formula_results.db"
    FormulaCalculationAgent("pyme_A", formula_db).calculate_and_persist(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=600),
        ],
        result_id="r1",
    )

    import app.mcp.tools.formula_results_tool as formula_tool
    import app.mcp.tools.jobs_read_tool as jobs_tool

    jobs_tool.Path = lambda p: tmp_path / "empty.db"
    formula_tool.Path = lambda p: formula_db

    status = get_owner_status("pyme_B")

    assert status["formula_results_count"] == 0
    assert status["formula_results"] == []
