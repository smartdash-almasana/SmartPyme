from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from app.ai.orchestrators.ai_intake_orchestrator import AIIntakeOrchestrator
from app.ai.schemas.soft_interpretation_result import SoftInterpretationResult
from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation


@pytest.fixture
def mock_consumer():
    return MagicMock()


@pytest.fixture
def mock_validator():
    return MagicMock()


@pytest.fixture
def mock_curator():
    return MagicMock()


@pytest.fixture
def orchestrator(mock_consumer, mock_validator, mock_curator):
    return AIIntakeOrchestrator(
        consumer=mock_consumer,
        validator=mock_validator,
        curator=mock_curator,
    )


def test_process_no_interpretation(orchestrator, mock_consumer):
    mock_consumer.consume.return_value = SoftInterpretationResult.failed(raw_message="test", errors=["error"])

    res = orchestrator.process_owner_message("test", "C1")

    assert res["status"] == "NO_INTERPRETATION"
    assert res["reason"] == "LLM_FAILURE"


def test_process_empty_interpretation(orchestrator, mock_consumer):
    mock_consumer.consume.return_value = SoftInterpretationResult.empty(raw_message="   ")

    res = orchestrator.process_owner_message("   ", "C1")

    assert res["status"] == "NO_INTERPRETATION"
    assert res["reason"] == "EMPTY_INPUT"


def test_process_no_intent(orchestrator, mock_consumer):
    inter = OwnerMessageInterpretation(intent=None)
    mock_consumer.consume.return_value = SoftInterpretationResult.ok(raw_message="test", interpretation=inter)

    res = orchestrator.process_owner_message("test", "C1")

    assert res["status"] == "NO_INTERPRETATION"
    assert res["reason"] == "NO_INTENT_DETECTED"


def test_process_conditions_ok_leads_to_job_proposal(orchestrator, mock_consumer, mock_validator, mock_curator):
    inter = OwnerMessageInterpretation(intent="skill_x", variables=["var1"], evidence=["ev1"])
    mock_consumer.consume.return_value = SoftInterpretationResult.ok(raw_message="test", interpretation=inter)

    mock_curator.curate_input.return_value = MagicMock(
        status="CURATION_OK",
        cleaned_payload={"variables": {"var1": True}, "evidence": ["ev1"]},
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "CONDITIONS_OK",
        "skill_id": "skill_x",
    }

    res = orchestrator.process_owner_message("test", "C1")

    assert res["status"] == "JOB_PROPOSAL"
    assert res["job_preview"]["skill_id"] == "skill_x"
    assert res["job_preview"]["cliente_id"] == "C1"
    assert res["job_preview"]["intent"] == "skill_x"
    assert "summary" in res["job_preview"]
    assert res["job_preview"]["raw_message"] == "test"
    # Ensure no interpretation dump
    assert "interpretation" not in res["job_preview"]


def test_process_conditions_missing_leads_to_clarification(orchestrator, mock_consumer, mock_validator, mock_curator):
    inter = OwnerMessageInterpretation(intent="skill_x")
    mock_consumer.consume.return_value = SoftInterpretationResult.ok(raw_message="test", interpretation=inter)

    mock_curator.curate_input.return_value = MagicMock(
        status="CURATION_OK",
        cleaned_payload={"variables": {}, "evidence": []},
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "CONDITIONS_MISSING",
        "skill_id": "skill_x",
        "missing_variables": ["var1"],
        "missing_evidence": ["ev1"],
    }

    res = orchestrator.process_owner_message("test", "C1")

    assert res["status"] == "CLARIFICATION_REQUIRED"
    assert res["skill_id"] == "skill_x"
    assert res["missing_variables"] == ["var1"]
    assert res["missing_evidence"] == ["ev1"]


def test_explicit_symptom_id_enriches_clarification_required(orchestrator, mock_consumer, mock_validator, mock_curator):
    inter = OwnerMessageInterpretation(
        intent="skill_margin_leak_audit",
        symptom_id="sospecha_perdida_margen",
    )
    mock_consumer.consume.return_value = SoftInterpretationResult.ok(raw_message="test", interpretation=inter)

    mock_curator.curate_input.return_value = MagicMock(
        status="CURATION_OK",
        cleaned_payload={"variables": {}, "evidence": []},
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "CONDITIONS_MISSING",
        "skill_id": "skill_margin_leak_audit",
        "missing_variables": ["periodo"],
        "missing_evidence": [],
    }

    res = orchestrator.process_owner_message("test", "C1")

    assert res["status"] == "CLARIFICATION_REQUIRED"
    assert res["symptom_id"] == "sospecha_perdida_margen"
    assert "productos_o_familias" in res["missing_variables"]
    assert "facturas_proveedor" in res["missing_evidence"]
    assert res["mayeutic_questions"]
    assert "symptom_catalog_context" in res
    assert "diagnostic_report" not in res
    assert "job_preview" not in res


def test_unknown_symptom_id_does_not_break_clarification(orchestrator, mock_consumer, mock_validator, mock_curator):
    inter = OwnerMessageInterpretation(intent="skill_x", symptom_id="symptom_inexistente")
    mock_consumer.consume.return_value = SoftInterpretationResult.ok(raw_message="test", interpretation=inter)

    mock_curator.curate_input.return_value = MagicMock(
        status="CURATION_OK",
        cleaned_payload={"variables": {}, "evidence": []},
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "CONDITIONS_MISSING",
        "skill_id": "skill_x",
        "missing_variables": ["var1"],
        "missing_evidence": ["ev1"],
    }

    res = orchestrator.process_owner_message("test", "C1")

    assert res["status"] == "CLARIFICATION_REQUIRED"
    assert res["missing_variables"] == ["var1"]
    assert res["missing_evidence"] == ["ev1"]
    assert "symptom_id" not in res
    assert "symptom_catalog_context" not in res


def test_explicit_symptom_id_does_not_change_job_proposal_flow(orchestrator, mock_consumer, mock_validator, mock_curator):
    inter = OwnerMessageInterpretation(
        intent="skill_margin_leak_audit",
        symptom_id="sospecha_perdida_margen",
    )
    mock_consumer.consume.return_value = SoftInterpretationResult.ok(raw_message="test", interpretation=inter)

    mock_curator.curate_input.return_value = MagicMock(
        status="CURATION_OK",
        cleaned_payload={"variables": {"periodo": True}, "evidence": ["facturas_proveedor"]},
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "CONDITIONS_OK",
        "skill_id": "skill_margin_leak_audit",
    }

    res = orchestrator.process_owner_message("test", "C1")

    assert res["status"] == "JOB_PROPOSAL"
    assert res["job_preview"]["skill_id"] == "skill_margin_leak_audit"
    assert "symptom_catalog_context" not in res
    assert "diagnostic_report" not in res


def test_process_conditions_invalid_leads_to_rejected(orchestrator, mock_consumer, mock_validator, mock_curator):
    inter = OwnerMessageInterpretation(intent="skill_x")
    mock_consumer.consume.return_value = SoftInterpretationResult.ok(raw_message="test", interpretation=inter)

    mock_curator.curate_input.return_value = MagicMock(
        status="CURATION_OK",
        cleaned_payload={"variables": {}, "evidence": []},
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "CONDITIONS_INVALID",
        "reason": "INVALID_INPUT_TYPES",
    }

    res = orchestrator.process_owner_message("test", "C1")

    assert res["status"] == "REJECTED"
    assert res["skill_id"] == "skill_x"
    assert res["error_type"] == "CONDITIONS_INVALID"
    assert res["reason"] == "INVALID_INPUT_TYPES"


def test_process_unknown_skill_leads_to_rejected(orchestrator, mock_consumer, mock_validator, mock_curator):
    inter = OwnerMessageInterpretation(intent="unknown_skill")
    mock_consumer.consume.return_value = SoftInterpretationResult.ok(raw_message="test", interpretation=inter)

    mock_curator.curate_input.return_value = MagicMock(
        status="CURATION_OK",
        cleaned_payload={"variables": {}, "evidence": []},
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "UNKNOWN_SKILL",
        "skill_id": "unknown_skill",
    }

    res = orchestrator.process_owner_message("test", "C1")

    assert res["status"] == "REJECTED"
    assert res["skill_id"] == "unknown_skill"
    assert res["error_type"] == "UNKNOWN_SKILL"


def test_process_curation_invalid_leads_to_rejected(orchestrator, mock_consumer, mock_curator):
    inter = OwnerMessageInterpretation(intent="skill_x")
    mock_consumer.consume.return_value = SoftInterpretationResult.ok(raw_message="test", interpretation=inter)

    mock_curator.curate_input.return_value = MagicMock(
        status="CURATION_INVALID",
        errors=["INVALID_RANGE: var1"],
    )

    res = orchestrator.process_owner_message("test", "C1")

    assert res["status"] == "REJECTED"
    assert res["error_type"] == "INVALID_INPUT"
    assert "INVALID_RANGE: var1" in res["reason"]
