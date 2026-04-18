from core.job import Job
from core.orchestrator import advance_job


def test_advance_job_moves_created_to_completed() -> None:
    job = Job.create()
    assert job.status == "created"

    result = advance_job(job)

    assert job.status == "created"
    assert result.status == "completed"
