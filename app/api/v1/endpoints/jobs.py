from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_active_client
from app.contracts.job_contract import Job
from app.repositories.job_repository import JobRepository

router = APIRouter()


class JobsDbPath(BaseModel):
    jobs: str


class CreateJobRequest(BaseModel):
    job_type: str = "MANUAL"
    payload: dict = Field(default_factory=dict)
    traceable_origin: dict = Field(default_factory=dict)


async def get_jobs_db_path() -> JobsDbPath:
    return JobsDbPath(jobs="data/jobs.db")


def serialize_job(job: Job) -> dict:
    return {
        "job_id": job.job_id,
        "cliente_id": job.cliente_id,
        "job_type": job.job_type,
        "status": job.status.value,
        "payload": job.payload,
        "result": job.result,
        "error_log": job.error_log,
        "traceable_origin": job.traceable_origin,
    }


@router.post("/jobs")
async def create_job(
    request: CreateJobRequest | None = None,
    cliente_id: str = Depends(get_active_client),
    db_path: JobsDbPath = Depends(get_jobs_db_path),
):
    request = request or CreateJobRequest()
    repo = JobRepository(cliente_id, Path(db_path.jobs))
    job = Job(
        job_id=str(uuid4()),
        cliente_id=cliente_id,
        job_type=request.job_type,
        payload=request.payload,
        traceable_origin=request.traceable_origin,
    )
    repo.create(job)

    return serialize_job(job)


@router.get("/jobs")
async def list_jobs(
    cliente_id: str = Depends(get_active_client),
    db_path: JobsDbPath = Depends(get_jobs_db_path),
):
    repo = JobRepository(cliente_id, Path(db_path.jobs))
    jobs = repo.list_jobs()

    return {
        "cliente_id": cliente_id,
        "count": len(jobs),
        "jobs": [serialize_job(job) for job in jobs],
    }


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    cliente_id: str = Depends(get_active_client),
    db_path: JobsDbPath = Depends(get_jobs_db_path),
):
    repo = JobRepository(cliente_id, Path(db_path.jobs))
    job = repo.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return serialize_job(job)
