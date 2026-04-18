from core.job import Job


def advance_job(job: Job) -> Job:
    if job.status == "created":
        return Job(id=job.id, status="completed")
    return Job(id=job.id, status=job.status)
