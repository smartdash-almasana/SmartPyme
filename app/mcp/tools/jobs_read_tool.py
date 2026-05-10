import os
from pathlib import Path

from app.repositories.finding_repository import FindingRepository
from app.repositories.job_repository import JobRepository


def get_jobs(cliente_id: str):
    repo = JobRepository(cliente_id, _jobs_db_path())
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
    repo = FindingRepository(cliente_id, _findings_db_path())
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


def _jobs_db_path() -> Path:
    return Path(os.getenv("SMARTPYME_JOBS_DB_PATH", "data/jobs.db"))


def _findings_db_path() -> Path:
    return Path(os.getenv("SMARTPYME_FINDINGS_DB_PATH", "data/findings.db"))
