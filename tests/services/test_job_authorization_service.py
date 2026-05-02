import pytest
from unittest.mock import MagicMock
from app.services.job_authorization_service import JobAuthorizationService
from app.contracts.decision_record import DecisionRecord

@pytest.fixture
def service():
    return JobAuthorizationService()

@pytest.fixture
def mock_job_repo():
    return MagicMock()

@pytest.fixture
def mock_decision_repo():
    return MagicMock()

def test_authorize_success_created(service, mock_job_repo, mock_decision_repo):
    job_id = "job_123"
    cliente_id = "C1"
    
    mock_job_repo.get_job.return_value = {
        "job_id": job_id,
        "status": "created",
        "payload": {"operational_plan": {"cliente_id": cliente_id}}
    }
    
    decision = DecisionRecord(
        decision_id="dec_001",
        cliente_id=cliente_id,
        timestamp="2026-05-01",
        tipo_decision="EJECUTAR",
        mensaje_original="Hacelo",
        propuesta={},
        accion="TEST",
        job_id=job_id
    )
    mock_decision_repo.list_by_cliente.return_value = [decision]
    
    res = service.authorize_job_execution(cliente_id, job_id, mock_job_repo, mock_decision_repo)
    assert res["status"] == "AUTHORIZED"
    assert res["decision_id"] == "dec_001"

def test_authorize_success_pending_confirmation(service, mock_job_repo, mock_decision_repo):
    job_id = "job_123"
    cliente_id = "C1"
    
    mock_job_repo.get_job.return_value = {
        "job_id": job_id,
        "status": "pending_owner_confirmation",
        "payload": {"operational_plan": {"cliente_id": cliente_id}}
    }
    
    decision = DecisionRecord(
        decision_id="dec_001",
        cliente_id=cliente_id,
        timestamp="2026-05-01",
        tipo_decision="EJECUTAR",
        mensaje_original="Hacelo",
        propuesta={},
        accion="TEST",
        job_id=job_id
    )
    mock_decision_repo.list_by_cliente.return_value = [decision]
    
    res = service.authorize_job_execution(cliente_id, job_id, mock_job_repo, mock_decision_repo)
    assert res["status"] == "AUTHORIZED"

def test_block_missing_decision(service, mock_job_repo, mock_decision_repo):
    job_id = "job_123"
    cliente_id = "C1"
    mock_job_repo.get_job.return_value = {
        "job_id": job_id,
        "status": "created",
        "payload": {"operational_plan": {"cliente_id": cliente_id}}
    }
    mock_decision_repo.list_by_cliente.return_value = []
    
    res = service.authorize_job_execution(cliente_id, job_id, mock_job_repo, mock_decision_repo)
    assert res["status"] == "NOT_AUTHORIZED"
    assert res["reason"] == "MISSING_DECISION"

def test_block_informar_decision(service, mock_job_repo, mock_decision_repo):
    job_id = "job_123"
    cliente_id = "C1"
    mock_job_repo.get_job.return_value = {
        "job_id": job_id,
        "status": "created",
        "payload": {"operational_plan": {"cliente_id": cliente_id}}
    }
    decision = DecisionRecord(
        decision_id="dec_001",
        cliente_id=cliente_id,
        timestamp="2026-05-01",
        tipo_decision="INFORMAR",
        mensaje_original="Solo avisame",
        propuesta={},
        accion="TEST",
        job_id=job_id
    )
    mock_decision_repo.list_by_cliente.return_value = [decision]
    
    res = service.authorize_job_execution(cliente_id, job_id, mock_job_repo, mock_decision_repo)
    assert res["status"] == "NOT_AUTHORIZED"
    assert res["reason"] == "MISSING_DECISION"

def test_block_rechazar_decision(service, mock_job_repo, mock_decision_repo):
    job_id = "job_123"
    cliente_id = "C1"
    mock_job_repo.get_job.return_value = {
        "job_id": job_id,
        "status": "created",
        "payload": {"operational_plan": {"cliente_id": cliente_id}}
    }
    decision = DecisionRecord(
        decision_id="dec_001",
        cliente_id=cliente_id,
        timestamp="2026-05-01",
        tipo_decision="RECHAZAR",
        mensaje_original="No quiero",
        propuesta={},
        accion="TEST",
        job_id=job_id
    )
    mock_decision_repo.list_by_cliente.return_value = [decision]
    
    res = service.authorize_job_execution(cliente_id, job_id, mock_job_repo, mock_decision_repo)
    assert res["status"] == "NOT_AUTHORIZED"
    assert res["reason"] == "MISSING_DECISION"

def test_block_job_not_found(service, mock_job_repo, mock_decision_repo):
    mock_job_repo.get_job.return_value = None
    res = service.authorize_job_execution("C1", "job_unknown", mock_job_repo, mock_decision_repo)
    assert res["status"] == "INVALID_STATE"
    assert res["reason"] == "JOB_NOT_FOUND"

def test_block_job_already_running(service, mock_job_repo, mock_decision_repo):
    job_id = "job_123"
    cliente_id = "C1"
    mock_job_repo.get_job.return_value = {
        "job_id": job_id,
        "status": "running",
        "payload": {"operational_plan": {"cliente_id": cliente_id}}
    }
    res = service.authorize_job_execution(cliente_id, job_id, mock_job_repo, mock_decision_repo)
    assert res["status"] == "INVALID_STATE"
    assert res["reason"] == "JOB_ALREADY_RUNNING"

def test_block_job_finished(service, mock_job_repo, mock_decision_repo):
    job_id = "job_123"
    cliente_id = "C1"
    for s in ["completed", "failed", "finished"]:
        mock_job_repo.get_job.return_value = {
            "job_id": job_id,
            "status": s,
            "payload": {"operational_plan": {"cliente_id": cliente_id}}
        }
        res = service.authorize_job_execution(cliente_id, job_id, mock_job_repo, mock_decision_repo)
        assert res["status"] == "INVALID_STATE"
        assert res["reason"] == "JOB_FINISHED"

def test_verify_client_isolation(service, mock_job_repo, mock_decision_repo):
    job_id = "job_123"
    mock_job_repo.get_job.return_value = {
        "job_id": job_id,
        "status": "created",
        "payload": {"operational_plan": {"cliente_id": "CLIENT_A"}}
    }
    
    # Requesting as CLIENT_B
    res = service.authorize_job_execution("CLIENT_B", job_id, mock_job_repo, mock_decision_repo)
    assert res["status"] == "INVALID_STATE"
    assert res["reason"] == "JOB_NOT_FOUND"
