from core.job import Job
from core.orchestrator import advance_job


def main() -> None:
    job = Job.create()
    job = advance_job(job)
    print(f"Job {job.id} -> {job.status}")


if __name__ == "__main__":
    main()
