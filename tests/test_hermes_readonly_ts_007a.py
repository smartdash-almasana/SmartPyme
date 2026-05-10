
from app.contracts.job_contract import Job
from app.mcp.tools.jobs_read_tool import get_findings, get_jobs
from app.repositories.finding_repository import FindingRepository
from app.repositories.job_repository import JobRepository
from app.services.findings_service import Finding


def test_hermes_read_sovereignty(tmp_path, monkeypatch):
    base = tmp_path

    cliente_a = "pyme_A"
    cliente_b = "pyme_B"

    jobs_db = base / "data" / "jobs.db"
    findings_db = base / "data" / "findings.db"
    formula_db = base / "data" / "formula_results.db"
    pathologies_db = base / "data" / "pathologies.db"
    monkeypatch.setenv("SMARTPYME_JOBS_DB_PATH", str(jobs_db))
    monkeypatch.setenv("SMARTPYME_FINDINGS_DB_PATH", str(findings_db))
    monkeypatch.setenv("SMARTPYME_FORMULA_RESULTS_DB_PATH", str(formula_db))
    monkeypatch.setenv("SMARTPYME_PATHOLOGIES_DB_PATH", str(pathologies_db))

    job_repo_a = JobRepository(cliente_a, jobs_db)
    finding_repo_a = FindingRepository(cliente_a, findings_db)

    job = Job(job_id="job1", cliente_id=cliente_a, job_type="TEST")
    job_repo_a.create(job)

    finding_repo_a.save(Finding(
        finding_id="f1",
        entity_id_a="a",
        entity_id_b="b",
        entity_type="test",
        metric="price",
        source_a_value=1,
        source_b_value=2,
        difference=1,
        difference_pct=100,
        severity="ALTO",
        suggested_action="review",
        traceable_origin={}
    ))

    jobs_a = get_jobs(cliente_a)
    findings_a = get_findings(cliente_a)

    assert len(jobs_a) == 1
    assert jobs_a[0]["job_id"] == "job1"

    assert len(findings_a) == 1
    assert findings_a[0]["finding_id"] == "f1"

    jobs_b = get_jobs(cliente_b)
    findings_b = get_findings(cliente_b)

    assert jobs_b == []
    assert findings_b == []
