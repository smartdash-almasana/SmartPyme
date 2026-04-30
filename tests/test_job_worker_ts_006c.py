from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.jobs import router, get_jobs_db_path, JobsDbPath


def create_app(db_jobs: Path):
    app = FastAPI()

    async def override_jobs_db():
        return JobsDbPath(jobs=str(db_jobs))

    app.dependency_overrides[get_jobs_db_path] = override_jobs_db
    app.include_router(router)

    return app


def test_job_executes(tmp_path):
    db = tmp_path / "jobs.db"
    client = TestClient(create_app(db))

    payload = {
        "evidence_id_a": "ev-a",
        "text_a": "Factura 20-12345678-3 por $1500.25",
        "evidence_id_b": "ev-b",
        "text_b": "Factura 20-12345678-3 por $1800.00"
    }

    res = client.post("/jobs", json={"payload": payload}, headers={"X-Client-ID": "pyme_A"})
    assert res.status_code == 200

    job_id = res.json()["job_id"]

    res_get = client.get(f"/jobs/{job_id}", headers={"X-Client-ID": "pyme_A"})
    assert res_get.status_code == 200


def test_job_isolation(tmp_path):
    db = tmp_path / "jobs.db"
    client = TestClient(create_app(db))

    payload = {
        "evidence_id_a": "ev-a",
        "text_a": "Factura 20-12345678-3 por $1500.25",
        "evidence_id_b": "ev-b",
        "text_b": "Factura 20-12345678-3 por $1800.00"
    }

    res = client.post("/jobs", json={"payload": payload}, headers={"X-Client-ID": "pyme_A"})
    job_id = res.json()["job_id"]

    res_other = client.get(f"/jobs/{job_id}", headers={"X-Client-ID": "pyme_B"})
    assert res_other.status_code == 404
