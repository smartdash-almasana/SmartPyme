import pytest
from unittest.mock import MagicMock
from app.services.job_executor_service import JobExecutorService
from app.services.job_authorization_service import JobAuthorizationService
from app.orchestrator.models import STATE_RUNNING


@pytest.fixture
def auth_service():
    return MagicMock(spec=JobAuthorizationService)


@pytest.fixture
def executor(auth_service):
    return JobExecutorService(auth_service=auth_service)


@pytest.fixture
def mock_job_repo():
    return MagicMock()


@pytest.fixture
def mock_decision_repo():
    return MagicMock()


def test_start_authorized_job_success(executor, auth_service, mock_job_repo, mock_decision_repo):
    job_id = "job_123"
    cliente_id = "C1"
    decision_id = "dec_999"
    
    # Mock Auth success
    auth_service.authorize_job_execution.return_value = {
        "status": "AUTHORIZED",
        "job_id": job_id,
        "decision_id": decision_id
    }
    
    # Mock Job Data
    mock_job_repo.get_job.return_value = {
        "job_id": job_id,
        "status": "created",
        "current_state": "CREATED",
        "skill_id": "test_skill",
        "payload": {"foo": "bar"}
    }
    
    res = executor.start_authorized_job(cliente_id, job_id, mock_job_repo, mock_decision_repo)
    
    assert res["status"] == "JOB_STARTED"
    assert res["job_id"] == job_id
    assert res["decision_id"] == decision_id
    
    # Verify save_job was called with RUNNING state
    args, _ = mock_job_repo.save_job.call_args
    job_saved = args[0]
    assert job_saved.job_id == job_id
    assert job_saved.current_state == STATE_RUNNING
    assert job_saved.status == "running"


def test_start_job_not_authorized_missing_decision(executor, auth_service, mock_job_repo, mock_decision_repo):
    # Mock Auth failure
    auth_service.authorize_job_execution.return_value = {
        "status": "NOT_AUTHORIZED",
        "reason": "MISSING_DECISION"
    }
    
    res = executor.start_authorized_job("C1", "job_123", mock_job_repo, mock_decision_repo)
    
    assert res["status"] == "NOT_AUTHORIZED"
    assert res["reason"] == "MISSING_DECISION"
    mock_job_repo.save_job.assert_not_called()


def test_start_job_not_authorized_informar(executor, auth_service, mock_job_repo, mock_decision_repo):
    # Mock Auth failure - even if it's type mismatch, logic should propagate
    auth_service.authorize_job_execution.return_value = {
        "status": "NOT_AUTHORIZED",
        "reason": "DECISION_TYPE_MISMATCH"
    }
    
    res = executor.start_authorized_job("C1", "job_123", mock_job_repo, mock_decision_repo)
    
    assert res["status"] == "NOT_AUTHORIZED"
    assert res["reason"] == "DECISION_TYPE_MISMATCH"
    mock_job_repo.save_job.assert_not_called()


def test_start_job_invalid_state_already_running(executor, auth_service, mock_job_repo, mock_decision_repo):
    # Mock Auth returns INVALID_STATE (e.g. already running)
    auth_service.authorize_job_execution.return_value = {
        "status": "INVALID_STATE",
        "reason": "JOB_ALREADY_RUNNING"
    }
    
    res = executor.start_authorized_job("C1", "job_123", mock_job_repo, mock_decision_repo)
    
    assert res["status"] == "INVALID_STATE"
    assert res["reason"] == "JOB_ALREADY_RUNNING"
    mock_job_repo.save_job.assert_not_called()


def test_start_job_invalid_state_finished(executor, auth_service, mock_job_repo, mock_decision_repo):
    # Mock Auth returns INVALID_STATE (e.g. finished)
    auth_service.authorize_job_execution.return_value = {
        "status": "INVALID_STATE",
        "reason": "JOB_FINISHED"
    }
    
    res = executor.start_authorized_job("C1", "job_123", mock_job_repo, mock_decision_repo)
    
    assert res["status"] == "INVALID_STATE"
    assert res["reason"] == "JOB_FINISHED"
    mock_job_repo.save_job.assert_not_called()


def test_start_job_not_found_post_auth(executor, auth_service, mock_job_repo, mock_decision_repo):
    # Auth says OK (rare but possible if deleted between calls)
    auth_service.authorize_job_execution.return_value = {
        "status": "AUTHORIZED",
        "job_id": "job_123",
        "decision_id": "dec_1"
    }
    mock_job_repo.get_job.return_value = None
    
    res = executor.start_authorized_job("C1", "job_123", mock_job_repo, mock_decision_repo)
    
    assert res["status"] == "INVALID_STATE"
    assert res["reason"] == "JOB_NOT_FOUND"
    mock_job_repo.save_job.assert_not_called()
