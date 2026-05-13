from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.ai.orchestrators.operational_case_orchestrator import OperationalCaseOrchestrator
from app.orchestrator.models import STATE_RUNNING


def _job_payload(**overrides):
    payload = {
        "job_id": "job-1",
        "current_state": STATE_RUNNING,
        "skill_id": "skill_reconciliation_v1",
        "payload": {
            "cliente_id": "C1",
            "objective": "existe duplicidad en facturas",
            "owner_request": "Revisar duplicados",
            "variables": {"period": "2024"},
            "evidence": ["ev-1"],
        },
    }
    payload.update(overrides)
    return payload


def test_build_operational_case_blocks_missing_execution_contract() -> None:
    orchestrator = OperationalCaseOrchestrator()
    job_repo = MagicMock()
    case_repo = MagicMock()
    job_repo.get_job.return_value = {"job_id": "job-1", "current_state": STATE_RUNNING}

    result = orchestrator.build_operational_case("C1", "job-1", job_repo, case_repo)

    assert result["status"] == "REJECTED"
    assert result["error_type"] == "INVALID_JOB_PAYLOAD"
    assert "EXECUTION_BLOCKED[build_operational_case.job]" in result["reason"]
    case_repo.create_case.assert_not_called()


def test_build_operational_case_blocks_blocked_job_before_persistence() -> None:
    orchestrator = OperationalCaseOrchestrator()
    job_repo = MagicMock()
    case_repo = MagicMock()
    job_repo.get_job.return_value = _job_payload(current_state="BLOCKED")

    result = orchestrator.build_operational_case("C1", "job-1", job_repo, case_repo)

    assert result["status"] == "REJECTED"
    assert result["error_type"] == "INVALID_JOB_PAYLOAD"
    assert "contract is not executable" in result["reason"]
    case_repo.create_case.assert_not_called()


def test_build_operational_case_blocks_nested_payload_needs_evidence() -> None:
    orchestrator = OperationalCaseOrchestrator()
    job_repo = MagicMock()
    case_repo = MagicMock()
    job_repo.get_job.return_value = _job_payload(
        payload={
            "cliente_id": "C1",
            "objective": "existe duplicidad en facturas",
            "owner_request": "Revisar duplicados",
            "variables": {"period": "2024"},
            "evidence": ["ev-1"],
            "status": "NEEDS_EVIDENCE",
        }
    )

    result = orchestrator.build_operational_case("C1", "job-1", job_repo, case_repo)

    assert result["status"] == "REJECTED"
    assert result["error_type"] == "INVALID_JOB_PAYLOAD"
    assert "build_operational_case.job.payload" in result["reason"]
    case_repo.create_case.assert_not_called()


def test_build_operational_case_accepts_executable_job() -> None:
    orchestrator = OperationalCaseOrchestrator()
    job_repo = MagicMock()
    case_repo = MagicMock()
    job_repo.get_job.return_value = _job_payload()

    with patch("app.ai.orchestrators.operational_case_orchestrator.SkillRegistry") as registry:
        registry.return_value.has_skill.return_value = True
        result = orchestrator.build_operational_case("C1", "job-1", job_repo, case_repo)

    assert result["status"] == "OPERATIONAL_CASE_CREATED"
    case_repo.create_case.assert_called_once()
