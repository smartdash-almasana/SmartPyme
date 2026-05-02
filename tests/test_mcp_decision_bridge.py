import pytest
import sqlite3
from mcp_smartpyme_bridge import factory_record_decision
from app.repositories.decision_repository import DecisionRepository

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "mcp_test_decisions.db"

@pytest.mark.anyio
async def test_mcp_record_informar(db_path):
    res = await factory_record_decision(
        cliente_id="C1",
        tipo_decision="INFORMAR",
        mensaje_original="Test MCP",
        propuesta={"foo": "bar"},
        accion="NOTIFY",
        db_path=str(db_path)
    )
    
    assert res["status"] == "DECISION_RECORDED"
    assert "decision_id" in res
    
    # Verify persistence
    repo = DecisionRepository(cliente_id="C1", db_path=db_path)
    fetched = repo.get(res["decision_id"])
    assert fetched.tipo_decision == "INFORMAR"
    assert fetched.mensaje_original == "Test MCP"

@pytest.mark.anyio
async def test_mcp_record_rechazar(db_path):
    res = await factory_record_decision(
        cliente_id="C1",
        tipo_decision="RECHAZAR",
        mensaje_original="Rechazo MCP",
        propuesta={"kill": "true"},
        accion="ABORT",
        db_path=str(db_path)
    )
    assert res["status"] == "DECISION_RECORDED"
    
    repo = DecisionRepository(cliente_id="C1", db_path=db_path)
    fetched = repo.get(res["decision_id"])
    assert fetched.tipo_decision == "RECHAZAR"

@pytest.mark.anyio
async def test_mcp_record_ejecutar_with_job(db_path):
    res = await factory_record_decision(
        cliente_id="C1",
        tipo_decision="EJECUTAR",
        mensaje_original="Ejecutar MCP",
        propuesta={"run": "now"},
        accion="EXECUTE",
        job_id="job_123",
        db_path=str(db_path)
    )
    assert res["status"] == "DECISION_RECORDED"
    
    repo = DecisionRepository(cliente_id="C1", db_path=db_path)
    fetched = repo.get(res["decision_id"])
    assert fetched.tipo_decision == "EJECUTAR"
    assert fetched.job_id == "job_123"

@pytest.mark.anyio
async def test_mcp_invalid_input(db_path):
    res = await factory_record_decision(
        cliente_id="C1",
        tipo_decision="BAD_TYPE",
        mensaje_original="...",
        propuesta={},
        accion="TEST",
        db_path=str(db_path)
    )
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "INVALID_DECISION_INPUT"
    assert "Invalid tipo_decision" in res["reason"]

@pytest.mark.anyio
async def test_mcp_internal_error(db_path):
    # Simulate internal error by providing a directory instead of a file for db_path
    db_path.mkdir() 
    res = await factory_record_decision(
        cliente_id="C1",
        tipo_decision="INFORMAR",
        mensaje_original="...",
        propuesta={},
        accion="TEST",
        db_path=str(db_path)
    )
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "INTERNAL_ERROR"
    assert "Persistence failed" in res["reason"]
