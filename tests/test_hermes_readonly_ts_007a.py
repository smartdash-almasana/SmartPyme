
from app.contracts.job_contract import Job
from app.mcp.tools.jobs_read_tool import get_findings, get_jobs
from app.repositories.finding_repository import FindingRepository
from app.repositories.job_repository import JobRepository
from app.services.findings_service import Finding


def test_hermes_read_sovereignty(tmp_path):
    base = tmp_path

    cliente_a = "pyme_A"
    cliente_b = "pyme_B"

    jobs_db = base / "jobs.db"
    findings_db = base / "findings.db"

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

    # override paths
    import app.mcp.tools.jobs_read_tool as tool
    tool.Path = lambda p: jobs_db if "jobs" in p else findings_db

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
