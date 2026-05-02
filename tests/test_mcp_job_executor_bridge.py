import pytest
import os
import sqlite3
from mcp_smartpyme_bridge import factory_start_authorized_job
from app.orchestrator.persistence import save_job, get_job, init_jobs_db
from app.orchestrator.models import Job, STATE_CREATED
from app.repositories.decision_repository import DecisionRepository
from app.contracts.decision_record import DecisionRecord

@pytest.fixture
def jobs_db(tmp_path):
    db = tmp_path / "mcp_jobs_test.db"
    os.environ["SMARTPYME_JOBS_DB"] = str(db)
    init_jobs_db()
    yield db
    if "SMARTPYME_JOBS_DB" in os.environ:
        del os.environ["SMARTPYME_JOBS_DB"]

@pytest.fixture
def decisions_db(tmp_path):
    db = tmp_path / "mcp_decisions_test.db"
    os.environ["SMARTPYME_DECISIONS_DB"] = str(db)
    yield db
    if "SMARTPYME_DECISIONS_DB" in os.environ:
        del os.environ["SMARTPYME_DECISIONS_DB"]

@pytest.mark.anyio
async def test_mcp_start_authorized_job_success(jobs_db, decisions_db):
    cliente_id = "C1"
    job_id = "job_123"
    
    # 1. Setup Job
    job = Job(
        job_id=job_id,
        current_state=STATE_CREATED,
        status="created",
        payload={"operational_plan": {"cliente_id": cliente_id}}
    )
    save_job(job)
    
    # 2. Setup Decision
    repo = DecisionRepository(cliente_id=cliente_id, db_path=decisions_db)
    decision = DecisionRecord(
        decision_id="dec_1",
        cliente_id=cliente_id,
        timestamp="2026-05-01",
        tipo_decision="EJECUTAR",
        mensaje_original="Go",
        propuesta={},
        accion="EXEC",
        job_id=job_id
    )
    repo.create(decision)
    
    # 3. Call MCP Tool
    res = await factory_start_authorized_job(cliente_id=cliente_id, job_id=job_id)
    
    assert res["status"] == "JOB_STARTED"
    assert res["job_id"] == job_id
    assert res["decision_id"] == "dec_1"
    
    # 4. Verify Job State change
    updated_job = get_job(job_id)
    assert updated_job["status"] == "running"
    assert updated_job["current_state"] == "RUNNING"

@pytest.mark.anyio
async def test_mcp_start_job_not_authorized(jobs_db, decisions_db):
    cliente_id = "C1"
    job_id = "job_456"
    
    job = Job(
        job_id=job_id,
        status="created",
        payload={"operational_plan": {"cliente_id": cliente_id}}
    )
    save_job(job)
    
    # No decision record created
    
    res = await factory_start_authorized_job(cliente_id=cliente_id, job_id=job_id)
    
    assert res["status"] == "NOT_AUTHORIZED"
    assert res["reason"] == "MISSING_DECISION"

@pytest.mark.anyio
async def test_mcp_start_job_invalid_state(jobs_db, decisions_db):
    cliente_id = "C1"
    job_id = "job_789"
    
    # Job already running
    job = Job(
        job_id=job_id,
        status="running",
        current_state="RUNNING",
        payload={"operational_plan": {"cliente_id": cliente_id}}
    )
    save_job(job)
    
    res = await factory_start_authorized_job(cliente_id=cliente_id, job_id=job_id)
    
    assert res["status"] == "INVALID_STATE"
    assert res["reason"] == "JOB_ALREADY_RUNNING"

@pytest.mark.anyio
async def test_mcp_executor_internal_error(jobs_db, decisions_db):
    # Simulate error by breaking the repo (providing a directory where a file is expected)
    broken_db = decisions_db.parent / "broken_dir"
    broken_db.mkdir()
    os.environ["SMARTPYME_DECISIONS_DB"] = str(broken_db)
    
    try:
        res = await factory_start_authorized_job(cliente_id="C1", job_id="any")
        assert res["status"] == "REJECTED"
        assert res["error_type"] == "INTERNAL_ERROR"
    finally:
        os.environ["SMARTPYME_DECISIONS_DB"] = str(decisions_db)
