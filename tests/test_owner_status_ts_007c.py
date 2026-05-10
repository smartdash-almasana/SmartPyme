from app.contracts.job_contract import Job
from app.contracts.formula_contract import FormulaResult, FormulaStatus
from app.contracts.pathology_contract import PathologyFinding, PathologySeverity, PathologyStatus
from app.mcp.tools.owner_status_tool import get_owner_status
from app.repositories.finding_repository import FindingRepository
from app.repositories.formula_result_repository import FormulaResultRepository
from app.repositories.job_repository import JobRepository
from app.repositories.pathology_repository import PathologyRepository
from app.services.findings_service import Finding


def test_owner_status_aggregation(tmp_path, monkeypatch):
    base = tmp_path / "data"
    cliente = "pyme_A"

    jobs_db = base / "jobs.db"
    findings_db = base / "findings.db"
    formula_db = base / "formula_results.db"
    pathologies_db = base / "pathologies.db"

    monkeypatch.setenv("SMARTPYME_JOBS_DB_PATH", str(jobs_db))
    monkeypatch.setenv("SMARTPYME_FINDINGS_DB_PATH", str(findings_db))
    monkeypatch.setenv("SMARTPYME_FORMULA_RESULTS_DB_PATH", str(formula_db))
    monkeypatch.setenv("SMARTPYME_PATHOLOGIES_DB_PATH", str(pathologies_db))
    job_repo = JobRepository(cliente, jobs_db)
    finding_repo = FindingRepository(cliente, findings_db)
    formula_repo = FormulaResultRepository(cliente, formula_db)
    pathology_repo = PathologyRepository(cliente, pathologies_db)

    job_repo.create(Job(job_id="job1", cliente_id=cliente, job_type="TEST"))

    finding_repo.save(Finding(
        finding_id="f1",
        entity_id_a="a",
        entity_id_b="b",
        entity_type="precio",
        metric="price",
        source_a_value=1,
        source_b_value=2,
        difference=1,
        difference_pct=100,
        severity="ALTO",
        suggested_action="revisar",
        traceable_origin={}
    ))

    formula_repo.save(
        "fr1",
        FormulaResult(
            formula_id="ganancia_bruta",
            status=FormulaStatus.OK,
            value=-200.0,
            inputs={"ventas": 1000.0, "costos": 1200.0},
            source_refs=["test:source"],
        ),
    )
    pathology_repo.save(
        "pf1",
        PathologyFinding(
            cliente_id=cliente,
            pathology_id="venta_bajo_costo",
            formula_result_id="fr1",
            formula_id="ganancia_bruta",
            status=PathologyStatus.ACTIVE,
            severity=PathologySeverity.HIGH,
            suggested_action="Revisar precio de venta",
            source_refs=["test:source"],
            explanation="La ganancia bruta es negativa.",
        ),
    )

    status = get_owner_status(cliente)

    assert status["jobs_count"] == 1
    assert status["findings_count"] == 1
    assert status["formula_results_count"] == 1
    assert status["pathology_findings_count"] == 1
    assert len(status["messages"]) == 3
