import asyncio
import uuid
from pathlib import Path

from mcp_smartpyme_bridge import create_job, get_job_status


def test_create_job_mcp_persists_created_job_in_temp_db(monkeypatch):
    tmp_dir = Path(__file__).resolve().parents[1] / "fixtures" / "tmp_create_job_mcp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    jobs_db = tmp_dir / f"jobs-{uuid.uuid4().hex[:8]}.db"

    monkeypatch.setenv("SMARTPYME_JOBS_DB", str(jobs_db))

    create_response = asyncio.run(
        create_job(
            cliente_id="cliente-test",
            owner_request="Necesito ordenar caja y gastos.",
            objective="Crear un plan operativo minimo.",
            period=None,
            operational_vectors=["caja", "gastos"],
            required_sources=["extracto_bancario"],
            acceptance_criteria=["job consultable en CREATED"],
        )
    )

    assert create_response["source"] == "real"
    assert create_response["status"] == "created"
    assert create_response["current_state"] == "CREATED"
    assert create_response["job_id"].startswith("job-")
    assert create_response["plan_id"].startswith("plan-")
    assert create_response["skill_id"] == "skill_create_job_from_plan"
    assert "warning" not in create_response

    status_response = asyncio.run(get_job_status(create_response["job_id"]))

    assert status_response["source"] == "real"
    assert status_response["job_id"] == create_response["job_id"]
    assert status_response["status"] == "created"
    assert status_response["current_state"] == "CREATED"
    assert status_response["skill_id"] == "skill_create_job_from_plan"
    assert status_response["plan_id"] == create_response["plan_id"]
    assert status_response["payload"]["operational_plan"]["plan_id"] == create_response["plan_id"]
    assert status_response["payload"]["operational_plan"]["cliente_id"] == "cliente-test"
