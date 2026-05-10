from app.contracts.formula_contract import FormulaInput
from app.contracts.job_contract import Job
from app.agents.formula_calculation_agent import FormulaCalculationAgent
from app.mcp.tools.owner_status_tool import get_owner_status
from app.repositories.job_repository import JobRepository


def test_owner_status_includes_formula_results(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    jobs_db = data_dir / "jobs.db"
    findings_db = data_dir / "findings.db"
    formula_db = data_dir / "formula_results.db"
    pathologies_db = data_dir / "pathologies.db"
    monkeypatch.setenv("SMARTPYME_JOBS_DB_PATH", str(jobs_db))
    monkeypatch.setenv("SMARTPYME_FINDINGS_DB_PATH", str(findings_db))
    monkeypatch.setenv("SMARTPYME_FORMULA_RESULTS_DB_PATH", str(formula_db))
    monkeypatch.setenv("SMARTPYME_PATHOLOGIES_DB_PATH", str(pathologies_db))

    JobRepository("pyme_A", jobs_db).create(Job(job_id="j1", cliente_id="pyme_A", job_type="TEST"))
    FormulaCalculationAgent("pyme_A", formula_db).calculate_and_persist(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=600, source_refs=["costos:1"]),
        ],
        result_id="r1",
    )

    status = get_owner_status("pyme_A")

    assert status["jobs_count"] == 1
    assert status["formula_results_count"] == 1
    assert len(status["formula_results"]) == 1
    assert any("ganancia_bruta" in msg for msg in status["messages"])


def test_owner_status_formula_results_are_isolated(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    jobs_db = data_dir / "jobs.db"
    findings_db = data_dir / "findings.db"
    formula_db = data_dir / "formula_results.db"
    pathologies_db = data_dir / "pathologies.db"
    monkeypatch.setenv("SMARTPYME_JOBS_DB_PATH", str(jobs_db))
    monkeypatch.setenv("SMARTPYME_FINDINGS_DB_PATH", str(findings_db))
    monkeypatch.setenv("SMARTPYME_FORMULA_RESULTS_DB_PATH", str(formula_db))
    monkeypatch.setenv("SMARTPYME_PATHOLOGIES_DB_PATH", str(pathologies_db))

    FormulaCalculationAgent("pyme_A", formula_db).calculate_and_persist(
        "ganancia_bruta",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=600),
        ],
        result_id="r1",
    )

    status = get_owner_status("pyme_B")

    assert status["formula_results_count"] == 0
    assert status["formula_results"] == []
