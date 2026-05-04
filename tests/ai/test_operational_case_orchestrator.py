import pytest
from unittest.mock import MagicMock, patch
from app.ai.orchestrators.operational_case_orchestrator import OperationalCaseOrchestrator
from app.orchestrator.models import STATE_RUNNING, STATE_CREATED


@pytest.fixture
def orchestrator():
    return OperationalCaseOrchestrator()


@pytest.fixture
def mock_job_repo():
    return MagicMock()


@pytest.fixture
def mock_case_repo():
    return MagicMock()

@pytest.fixture(autouse=True)
def mock_skill_registry():
    """Mock SkillRegistry globally to avoid dependency on real catalog."""
    with patch('app.ai.orchestrators.operational_case_orchestrator.SkillRegistry') as mock_registry:
        mock_registry.return_value.has_skill.return_value = True
        yield mock_registry


def test_build_case_success(orchestrator, mock_job_repo, mock_case_repo):
    cliente_id = "C1"
    job_id = "job-123"
    
    mock_job_repo.get_job.return_value = {
        "job_id": job_id,
        "current_state": STATE_RUNNING,
        "skill_id": "skill_reconciliation_v1",
        "payload": {
            "cliente_id": cliente_id,
            "objective": "existe duplicidad en facturas",
            "owner_request": "Revisar duplicados",
            "variables": {"period": "2024"},
            "evidence": ["ev-1"],
            "symptom_id": "SYMPTOM-DUP"
        }
    }
    
    res = orchestrator.build_operational_case(cliente_id, job_id, mock_job_repo, mock_case_repo)
    
    assert res["status"] == "OPERATIONAL_CASE_CREATED"
    assert "case_id" in res    # Verify persistence call
    args, _ = mock_case_repo.create_case.call_args
    case = args[0]
    assert case.cliente_id == cliente_id
    assert case.job_id == job_id
    assert case.hypothesis == "Investigar si existe duplicidad en facturas?"
    assert case.status == "OPEN"
    assert case.evidence_ids == ["ev-1"]


def test_build_case_success_no_symptom(orchestrator, mock_job_repo, mock_case_repo):
    cliente_id = "C1"
    job_id = "job-124"
    
    mock_job_repo.get_job.return_value = {
        "job_id": job_id,
        "current_state": STATE_RUNNING,
        "skill_id": "skill_reconciliation_v1",
        "payload": {
            "cliente_id": cliente_id,
            "objective": "existe duplicidad en facturas",
            "owner_request": "Revisar duplicados",
            "variables": {"period": "2024"},
            "evidence": ["ev-1"]
            # No symptom_id in payload
        }
    }
    
    res = orchestrator.build_operational_case(cliente_id, job_id, mock_job_repo, mock_case_repo)
    
    assert res["status"] == "OPERATIONAL_CASE_CREATED"
    assert "case_id" in res    # Verify persistence call
    args, _ = mock_case_repo.create_case.call_args
    case = args[0]
    assert case.cliente_id == cliente_id
    assert case.job_id == job_id
    assert case.hypothesis == "Investigar si existe duplicidad en facturas?"
    assert case.status == "OPEN"
    assert case.evidence_ids == ["ev-1"]


def test_build_case_clarification_missing_demanda(orchestrator, mock_job_repo, mock_case_repo):
    mock_job_repo.get_job.return_value = {
        "job_id": "j1",
        "current_state": STATE_RUNNING,
        "skill_id": "s1",
        "payload": {
            "cliente_id": "C1",
            "variables": {"v": 1}
            # No objective and no owner_request
        }
    }
    res = orchestrator.build_operational_case("C1", "j1", mock_job_repo, mock_case_repo)
    assert res["status"] == "CLARIFICATION_REQUIRED"
    assert "demanda_original" in res["missing"]
    assert "qué querés investigar" in res["owner_message"]
    mock_case_repo.create_case.assert_not_called()


def test_build_case_clarification_missing_skill(orchestrator, mock_job_repo, mock_case_repo):
    mock_job_repo.get_job.return_value = {
        "job_id": "j1",
        "current_state": STATE_RUNNING,
        "skill_id": None, # Missing skill
        "payload": {
            "cliente_id": "C1",
            "objective": "test",
            "evidence": ["ev-1"]
        }
    }
    res = orchestrator.build_operational_case("C1", "j1", mock_job_repo, mock_case_repo)
    assert res["status"] == "CLARIFICATION_REQUIRED"
    assert "skill_id" in res["missing"]
    assert "qué tipo de trabajo" in res["owner_message"]
    mock_case_repo.create_case.assert_not_called()


def test_build_case_clarification_missing_context(orchestrator, mock_job_repo, mock_case_repo):
    mock_job_repo.get_job.return_value = {
        "job_id": "j1",
        "current_state": STATE_RUNNING,
        "skill_id": "s1",
        "payload": {
            "cliente_id": "C1",
            "objective": "test"
            # Missing variables AND evidence
        }
    }
    res = orchestrator.build_operational_case("C1", "j1", mock_job_repo, mock_case_repo)
    assert res["status"] == "CLARIFICATION_REQUIRED"
    assert "variables_curadas" in res["missing"]
    assert "evidencia_disponible" in res["missing"]
    assert "al menos datos concretos" in res["owner_message"]
    mock_case_repo.create_case.assert_not_called()


def test_build_case_rejected_not_running(orchestrator, mock_job_repo, mock_case_repo):
    mock_job_repo.get_job.return_value = {
        "job_id": "j1",
        "current_state": STATE_CREATED,
        "payload": {"cliente_id": "C1", "objective": "test"}
    }
    
    res = orchestrator.build_operational_case("C1", "j1", mock_job_repo, mock_case_repo)
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "JOB_NOT_RUNNING"


def test_build_case_rejected_not_found(orchestrator, mock_job_repo, mock_case_repo):
    mock_job_repo.get_job.return_value = None
    res = orchestrator.build_operational_case("C1", "unknown", mock_job_repo, mock_case_repo)
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "JOB_NOT_FOUND"


def test_build_case_rejected_isolation_violation(orchestrator, mock_job_repo, mock_case_repo):
    mock_job_repo.get_job.return_value = {
        "job_id": "j1",
        "current_state": STATE_RUNNING,
        "payload": {"cliente_id": "CLIENT_A", "objective": "test"}
    }
    # Requesting as CLIENT_B
    res = orchestrator.build_operational_case("CLIENT_B", "j1", mock_job_repo, mock_case_repo)
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "JOB_NOT_FOUND"


def test_build_case_real_persistence(orchestrator, mock_job_repo, tmp_path):
    # Using real OperationalCaseRepository for verification
    from app.repositories.operational_case_repository import OperationalCaseRepository
    db_path = tmp_path / "cases.db"
    case_repo = OperationalCaseRepository(cliente_id="C1", db_path=db_path)
    
    mock_job_repo.get_job.return_value = {
        "job_id": "j1",
        "current_state": STATE_RUNNING,
        "skill_id": "s1",
        "payload": {
            "cliente_id": "C1", 
            "objective": "analizar margen",
            "evidence": ["ev-1"]
        }
    }
    
    res = orchestrator.build_operational_case("C1", "j1", mock_job_repo, case_repo)
    assert res["status"] == "OPERATIONAL_CASE_CREATED"
    
    # Check physical DB
    fetched = case_repo.get_case(res["case_id"])
    assert fetched is not None
    assert fetched.hypothesis == "Investigar si analizar margen?"
