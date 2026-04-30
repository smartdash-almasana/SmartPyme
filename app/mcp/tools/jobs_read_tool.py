from pathlib import Path

from app.repositories.job_repository import JobRepository
from app.repositories.finding_repository import FindingRepository


def get_jobs(cliente_id: str):
    repo = JobRepository(cliente_id, Path("data/jobs.db"))
    jobs = repo.list_jobs()
    return [
        {
            "job_id": j.job_id,
            "status": j.status.value,
            "job_type": j.job_type,
        }
        for j in jobs
    ]


def get_findings(cliente_id: str):
    repo = FindingRepository(cliente_id, Path("data/findings.db"))
    findings = repo.list_findings()
    return [
        {
            "finding_id": f.finding_id,
            "entity_type": f.entity_type,
            "severity": f.severity,
            "difference": f.difference,
        }
        for f in findings
    ]
