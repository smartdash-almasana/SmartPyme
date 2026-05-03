import pytest
from unittest.mock import MagicMock
from app.ai.orchestrators.ai_intake_orchestrator import AIIntakeOrchestrator

def test_ai_intake_symptom_validation():
    # Mock dependencies
    mock_consumer = MagicMock()
    orchestrator = AIIntakeOrchestrator(consumer=mock_consumer)
    
    # 1. Caso: Symptom_id inválido
    mock_interpretation = MagicMock()
    mock_interpretation.intent = "some_skill"
    mock_interpretation.symptom_id = "sintoma_inexistente"
    mock_interpretation.variables = []
    mock_interpretation.evidence = []
    
    mock_consumer.consume.return_value.status = "success"
    mock_consumer.consume.return_value.interpretation = mock_interpretation
    
    result = orchestrator.process_owner_message("test message", "cliente123")
    
    assert result["status"] == "CLARIFICATION_REQUIRED"
    assert result["reason"] == "INVALID_SYMPTOM"
    
    # 2. Caso: Symptom_id inexistente (no debería bloquear si no se detecta síntoma)
    mock_interpretation.symptom_id = None
    # Necesitamos mockear la curación porque ahora pasará al paso 2
    mock_curator = MagicMock()
    mock_curator.curate_input.return_value.status = "CURATION_OK"
    mock_curator.curate_input.return_value.cleaned_payload = {"variables": {}, "evidence": []}
    orchestrator._curator = mock_curator
    
    mock_validator = MagicMock()
    mock_validator.validate_operational_conditions.return_value = {"status": "CONDITIONS_OK"}
    orchestrator._validator = mock_validator

    result = orchestrator.process_owner_message("test message", "cliente123")
    assert result["status"] == "JOB_PROPOSAL"

    # 3. Caso: Symptom_id válido
    mock_interpretation.symptom_id = "sospecha_perdida_margen"
    result = orchestrator.process_owner_message("test message", "cliente123")
    assert result["status"] == "JOB_PROPOSAL"
