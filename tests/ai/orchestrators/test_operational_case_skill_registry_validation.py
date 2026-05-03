import pytest
from unittest.mock import MagicMock
from app.ai.orchestrators.operational_case_orchestrator import OperationalCaseOrchestrator

class MockRepo:
    def get_job(self, job_id):
        return {
            "current_state": "RUNNING",
            "cliente_id": "C1",
            "skill_id": "skill_margin_leak_audit",
            "payload": {}
        }
    def create_case(self, case): pass

def test_invalid_skill_id_returns_clarification():
    orchestrator = OperationalCaseOrchestrator()
    repo = MockRepo()
    repo.get_job = MagicMock(return_value={
        "current_state": "RUNNING",
        "skill_id": "skill_invalid",
        "payload": {"cliente_id": "C1", "owner_request": "investigar margen", "variables": {"periodo": "2024-01"}}
    })
    result = orchestrator.build_operational_case("C1", "j1", repo, repo)
    assert result["status"] == "CLARIFICATION_REQUIRED"
    assert result["reason"] == "INVALID_SKILL_ID"

def test_valid_skill_id_passes():
    orchestrator = OperationalCaseOrchestrator()
    repo = MockRepo()
    repo.get_job = MagicMock(return_value={
        "current_state": "RUNNING",
        "skill_id": "skill_margin_leak_audit",
        "payload": {"cliente_id": "C1", "owner_request": "investigar margen", "variables": {"periodo": "2024-01"}}
    })
    # Mocking creation to succeed
    repo.create_case = MagicMock()
    result = orchestrator.build_operational_case("C1", "j1", repo, repo)
    assert result["status"] == "OPERATIONAL_CASE_CREATED"
