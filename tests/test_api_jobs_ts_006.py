from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.jobs import JobsDbPath, get_jobs_db_path, router


def create_app(db_jobs: Path):
    app = FastAPI()

    async def override_jobs_db():
        return JobsDbPath(jobs=str(db_jobs))

    app.dependency_overrides[get_jobs_db_path] = override_jobs_db
    app.include_router(router)

    return app


def test_jobs_requires_header(tmp_path):
    db = tmp_path / "jobs.db"
    client = TestClient(create_app(db))

    res = client.get("/jobs")
    assert res.status_code == 403


def test_create_and_get_job(tmp_path):
    db = tmp_path / "jobs.db"
    client = TestClient(create_app(db))

    res = client.post("/jobs", headers={"X-Client-ID": "pyme_A"})
    assert res.status_code in (200, 201)

    job = res.json()
    job_id = job["job_id"]

    res_get = client.get(f"/jobs/{job_id}", headers={"X-Client-ID": "pyme_A"})
    assert res_get.status_code == 200


def test_jobs_isolation(tmp_path):
    db = tmp_path / "jobs.db"
    client = TestClient(create_app(db))

    res = client.post("/jobs", headers={"X-Client-ID": "pyme_A"})
    job_id = res.json()["job_id"]

    res_other = client.get(f"/jobs/{job_id}", headers={"X-Client-ID": "pyme_B"})
    assert res_other.status_code == 404
