import pytest
import sqlite3
from app.ai.orchestrators.decision_orchestrator import DecisionOrchestrator, record_owner_decision
from app.repositories.decision_repository import DecisionRepository

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_decisions_orchestrator.db"

@pytest.fixture
def orchestrator():
    return DecisionOrchestrator()

def test_record_informar_without_job_id(db_path, orchestrator):
    input_data = {
        "tipo_decision": "INFORMAR",
        "mensaje_original": "Solo avisame",
        "propuesta": {"info": "abc"},
        "accion": "NOTIFICAR",
        "overrides": None,
        "job_id": None
    }
    
    res = orchestrator.record_owner_decision(input_data, "C1", str(db_path))
    
    assert res["status"] == "DECISION_RECORDED"
    decision_id = res["decision_id"]
    
    # Verify persistence
    repo = DecisionRepository(cliente_id="C1", db_path=db_path)
    fetched = repo.get(decision_id)
    assert fetched.tipo_decision == "INFORMAR"
    assert fetched.mensaje_original == "Solo avisame"
    assert fetched.job_id is None

def test_record_rechazar_without_job_id(db_path, orchestrator):
    input_data = {
        "tipo_decision": "RECHAZAR",
        "mensaje_original": "No quiero esto",
        "propuesta": {"action": "delete"},
        "accion": "DELETE",
        "overrides": None,
        "job_id": None
    }
    
    res = orchestrator.record_owner_decision(input_data, "C1", str(db_path))
    assert res["status"] == "DECISION_RECORDED"
    
    repo = DecisionRepository(cliente_id="C1", db_path=db_path)
    fetched = repo.get(res["decision_id"])
    assert fetched.tipo_decision == "RECHAZAR"

def test_record_ejecutar_with_job_id(db_path, orchestrator):
    input_data = {
        "tipo_decision": "EJECUTAR",
        "mensaje_original": "Hacelo",
        "propuesta": {"task": "fix"},
        "accion": "FIX",
        "overrides": {"priority": "high"},
        "job_id": "job_999"
    }
    
    res = orchestrator.record_owner_decision(input_data, "C1", str(db_path))
    assert res["status"] == "DECISION_RECORDED"
    
    repo = DecisionRepository(cliente_id="C1", db_path=db_path)
    fetched = repo.get(res["decision_id"])
    assert fetched.tipo_decision == "EJECUTAR"
    assert fetched.job_id == "job_999"
    assert fetched.overrides == {"priority": "high"}

def test_reject_invalid_tipo_decision(db_path, orchestrator):
    input_data = {
        "tipo_decision": "INVALID",
        "mensaje_original": "...",
        "propuesta": {},
        "accion": "TEST"
    }
    res = orchestrator.record_owner_decision(input_data, "C1", str(db_path))
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "INVALID_INPUT"
    assert "Invalid tipo_decision" in res["reason"]

def test_reject_proposal_not_dict(db_path, orchestrator):
    input_data = {
        "tipo_decision": "INFORMAR",
        "mensaje_original": "...",
        "propuesta": "not-a-dict",
        "accion": "TEST"
    }
    res = orchestrator.record_owner_decision(input_data, "C1", str(db_path))
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "INVALID_INPUT"
    assert "must be a dictionary" in res["reason"]

def test_reject_missing_mensaje_original(db_path, orchestrator):
    input_data = {
        "tipo_decision": "INFORMAR",
        "mensaje_original": "",
        "propuesta": {},
        "accion": "TEST"
    }
    res = orchestrator.record_owner_decision(input_data, "C1", str(db_path))
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "INVALID_INPUT"
    assert "mensaje_original is required" in res["reason"]

def test_reject_missing_accion(db_path, orchestrator):
    input_data = {
        "tipo_decision": "INFORMAR",
        "mensaje_original": "...",
        "propuesta": {},
        "accion": ""
    }
    res = orchestrator.record_owner_decision(input_data, "C1", str(db_path))
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "INVALID_INPUT"
    assert "accion is required" in res["reason"]

def test_reject_invalid_overrides(db_path, orchestrator):
    input_data = {
        "tipo_decision": "INFORMAR",
        "mensaje_original": "...",
        "propuesta": {},
        "accion": "TEST",
        "overrides": "not-a-dict"
    }
    res = orchestrator.record_owner_decision(input_data, "C1", str(db_path))
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "INVALID_INPUT"
    assert "overrides must be a dictionary or None" in res["reason"]

def test_standalone_function(db_path):
    input_data = {
        "tipo_decision": "INFORMAR",
        "mensaje_original": "...",
        "propuesta": {},
        "accion": "TEST"
    }
    res = record_owner_decision(input_data, "C1", str(db_path))
    assert res["status"] == "DECISION_RECORDED"

def test_cliente_id_isolation(db_path, orchestrator):
    input_data = {
        "tipo_decision": "INFORMAR",
        "mensaje_original": "Msg for C1",
        "propuesta": {},
        "accion": "TEST"
    }
    # Record for C1
    res1 = orchestrator.record_owner_decision(input_data, "C1", str(db_path))
    dec1 = res1["decision_id"]
    
    # Record for C2
    input_data["mensaje_original"] = "Msg for C2"
    res2 = orchestrator.record_owner_decision(input_data, "C2", str(db_path))
    dec2 = res2["decision_id"]
    
    # Verify C1 cannot see C2
    repo1 = DecisionRepository(cliente_id="C1", db_path=db_path)
    assert repo1.get(dec1) is not None
    assert repo1.get(dec2) is None
    
    # Verify C2 cannot see C1
    repo2 = DecisionRepository(cliente_id="C2", db_path=db_path)
    assert repo2.get(dec2) is not None
    assert repo2.get(dec1) is None
