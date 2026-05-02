import pytest
import os
from mcp_smartpyme_bridge import factory_build_operational_case
from app.orchestrator.persistence import save_job, init_jobs_db
from app.orchestrator.models import Job, STATE_RUNNING, STATE_CREATED
from app.repositories.operational_case_repository import OperationalCaseRepository

@pytest.fixture
def jobs_db(tmp_path):
    db = tmp_path / "mcp_jobs_cases_test.db"
    os.environ["SMARTPYME_JOBS_DB"] = str(db)
    init_jobs_db()
    yield db
    if "SMARTPYME_JOBS_DB" in os.environ:
        del os.environ["SMARTPYME_JOBS_DB"]

@pytest.fixture
def cases_db(tmp_path):
    db = tmp_path / "mcp_operational_cases_test.db"
    os.environ["SMARTPYME_CASES_DB"] = str(db)
    yield db
    if "SMARTPYME_CASES_DB" in os.environ:
        del os.environ["SMARTPYME_CASES_DB"]

@pytest.mark.anyio
async def test_mcp_build_operational_case_success(jobs_db, cases_db):
    cliente_id = "C1"
    job_id = "job-101"
    
    # 1. Setup Job RUNNING with enough context
    job = Job(
        job_id=job_id,
        current_state=STATE_RUNNING,
        status="running",
        skill_id="s1",
        payload={
            "cliente_id": cliente_id,
            "objective": "analizar margen",
            "evidence": ["ev-1"]
        }
    )
    save_job(job)
    
    # 2. Call MCP Tool
    res = await factory_build_operational_case(cliente_id=cliente_id, job_id=job_id)
    
    assert res["status"] == "OPERATIONAL_CASE_CREATED"
    assert "case_id" in res
    assert res["job_id"] == job_id
    
    # 3. Verify persistence
    repo = OperationalCaseRepository(cliente_id=cliente_id, db_path=cases_db)
    fetched = repo.get_case(res["case_id"])
    assert fetched is not None
    assert fetched.hypothesis == "Investigar si analizar margen?"

@pytest.mark.anyio
async def test_mcp_build_case_clarification(jobs_db, cases_db):
    cliente_id = "C1"
    job_id = "job-102"
    
    # Job RUNNING but missing context (evidence/variables)
    job = Job(
        job_id=job_id,
        current_state=STATE_RUNNING,
        status="running",
        skill_id="s1",
        payload={
            "cliente_id": cliente_id,
            "objective": "test"
            # Missing context
        }
    )
    save_job(job)
    
    res = await factory_build_operational_case(cliente_id=cliente_id, job_id=job_id)
    
    assert res["status"] == "CLARIFICATION_REQUIRED"
    assert "owner_message" in res
    assert "evidencia_disponible" in res["missing"]

@pytest.mark.anyio
async def test_mcp_build_case_rejected_not_found(jobs_db, cases_db):
    res = await factory_build_operational_case(cliente_id="C1", job_id="unknown")
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "JOB_NOT_FOUND"

@pytest.mark.anyio
async def test_mcp_build_case_rejected_not_running(jobs_db, cases_db):
    cliente_id = "C1"
    job_id = "job-103"
    
    job = Job(
        job_id=job_id,
        current_state=STATE_CREATED,
        status="created",
        payload={"cliente_id": cliente_id, "objective": "test"}
    )
    save_job(job)
    
    res = await factory_build_operational_case(cliente_id=cliente_id, job_id=job_id)
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "JOB_NOT_RUNNING"

@pytest.mark.anyio
async def test_mcp_build_case_internal_error(jobs_db, cases_db):
    # Broken DB path (directory instead of file)
    broken_db = cases_db.parent / "broken_cases_dir"
    broken_db.mkdir()
    os.environ["SMARTPYME_CASES_DB"] = str(broken_db)
    
    try:
        res = await factory_build_operational_case(cliente_id="C1", job_id="any")
        assert res["status"] == "REJECTED"
        assert res["error_type"] == "INTERNAL_ERROR"
    finally:
        os.environ["SMARTPYME_CASES_DB"] = str(cases_db)
