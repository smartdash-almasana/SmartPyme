from pathlib import Path

from app.mcp.tools.owner_status_tool import get_owner_status
from app.repositories.job_repository import JobRepository
from app.repositories.finding_repository import FindingRepository
from app.contracts.job_contract import Job
from app.services.findings_service import Finding


def test_owner_status_aggregation(tmp_path):
    base = tmp_path
    cliente = "pyme_A"

    jobs_db = base / "jobs.db"
    findings_db = base / "findings.db"

    job_repo = JobRepository(cliente, jobs_db)
    finding_repo = FindingRepository(cliente, findings_db)

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

    # override paths
    import app.mcp.tools.jobs_read_tool as tool
    tool.Path = lambda p: jobs_db if "jobs" in p else findings_db

    status = get_owner_status(cliente)

    assert status["jobs_count"] == 1
    assert status["findings_count"] == 1
    assert len(status["messages"]) == 1
