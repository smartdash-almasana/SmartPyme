from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.ai.orchestrators.decision_orchestrator import DecisionOrchestrator


def _decision_payload(**overrides):
    payload = {
        "tipo_decision": "EJECUTAR",
        "mensaje_original": "Ejecutar revisión",
        "propuesta": {"accion": "revisar", "target": "margen"},
        "accion": "crear_job",
        "overrides": {"objective": "analizar margen"},
        "job_id": "job-1",
    }
    payload.update(overrides)
    return payload


def test_record_owner_decision_blocks_blocked_overrides_before_persistence() -> None:
    orchestrator = DecisionOrchestrator()
    input_data = _decision_payload(overrides={"status": "BLOCKED"})

    with patch("app.ai.orchestrators.decision_orchestrator.DecisionRepository") as repo_cls:
        repo_cls.return_value.create = MagicMock()
        result = orchestrator.record_owner_decision(input_data, "C1", ":memory:")

    assert result["status"] == "REJECTED"
    assert result["error_type"] == "INVALID_DECISION_PAYLOAD"
    assert "record_owner_decision.input.overrides" in result["reason"]
    repo_cls.return_value.create.assert_not_called()


def test_record_owner_decision_blocks_blocked_propuesta_before_persistence() -> None:
    orchestrator = DecisionOrchestrator()
    input_data = _decision_payload(propuesta={"status": "NEEDS_EVIDENCE"})

    with patch("app.ai.orchestrators.decision_orchestrator.DecisionRepository") as repo_cls:
        repo_cls.return_value.create = MagicMock()
        result = orchestrator.record_owner_decision(input_data, "C1", ":memory:")

    assert result["status"] == "REJECTED"
    assert result["error_type"] == "INVALID_DECISION_PAYLOAD"
    assert "record_owner_decision.input.propuesta" in result["reason"]
    repo_cls.return_value.create.assert_not_called()


def test_record_owner_decision_accepts_executable_payload() -> None:
    orchestrator = DecisionOrchestrator()
    input_data = _decision_payload()

    with patch("app.ai.orchestrators.decision_orchestrator.DecisionRepository") as repo_cls:
        repo_cls.return_value.create = MagicMock()
        result = orchestrator.record_owner_decision(input_data, "C1", ":memory:")

    assert result["status"] == "DECISION_RECORDED"
    repo_cls.return_value.create.assert_called_once()
