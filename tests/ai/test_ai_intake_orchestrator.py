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
        curator=mock_curator
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
        cleaned_payload={"variables": {"var1": True}, "evidence": ["ev1"]}
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "CONDITIONS_OK",
        "skill_id": "skill_x"
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
        cleaned_payload={"variables": {}, "evidence": []}
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "CONDITIONS_MISSING",
        "skill_id": "skill_x",
        "missing_variables": ["var1"],
        "missing_evidence": ["ev1"]
    }
    
    res = orchestrator.process_owner_message("test", "C1")
    
    assert res["status"] == "CLARIFICATION_REQUIRED"
    assert res["skill_id"] == "skill_x"
    assert res["missing_variables"] == ["var1"]
    assert res["missing_evidence"] == ["ev1"]

def test_process_conditions_invalid_leads_to_rejected(orchestrator, mock_consumer, mock_validator, mock_curator):
    inter = OwnerMessageInterpretation(intent="skill_x")
    mock_consumer.consume.return_value = SoftInterpretationResult.ok(raw_message="test", interpretation=inter)
    
    mock_curator.curate_input.return_value = MagicMock(
        status="CURATION_OK",
        cleaned_payload={"variables": {}, "evidence": []}
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "CONDITIONS_INVALID",
        "reason": "INVALID_INPUT_TYPES"
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
        cleaned_payload={"variables": {}, "evidence": []}
    )

    mock_validator.validate_operational_conditions.return_value = {
        "status": "UNKNOWN_SKILL",
        "skill_id": "unknown_skill"
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
        errors=["INVALID_RANGE: var1"]
    )

    res = orchestrator.process_owner_message("test", "C1")
    
    assert res["status"] == "REJECTED"
    assert res["error_type"] == "INVALID_INPUT"
    assert "INVALID_RANGE: var1" in res["reason"]
