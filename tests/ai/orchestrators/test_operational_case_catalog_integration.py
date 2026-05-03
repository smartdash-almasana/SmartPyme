import pytest
from unittest.mock import MagicMock
from app.ai.orchestrators.operational_case_orchestrator import OperationalCaseOrchestrator

def test_operational_case_catalog_integration():
    orchestrator = OperationalCaseOrchestrator()
    mock_job_repo = MagicMock()
    mock_case_repo = MagicMock()
    
    # Simular Job con symptom_id válido y sin objective
    mock_job_repo.get_job.return_value = {
        "current_state": "RUNNING",
        "skill_id": "skill_margin_leak_audit",
        "payload": {
            "cliente_id": "cliente123",
            "symptom_id": "sospecha_perdida_margen",
            "variables": {"periodo": "2024-01"}
        }
    }
    
    result = orchestrator.build_operational_case("cliente123", "job123", mock_job_repo, mock_case_repo)
    
    assert result["status"] == "OPERATIONAL_CASE_CREATED"
    
    # Verificar que el repository fue llamado con un caso enriquecido
    case = mock_case_repo.create_case.call_args[0][0]
    
    assert case.symptom_id_orientativo == "sospecha_perdida_margen"
    assert case.skill_id == "skill_margin_leak_audit" 
    assert "Investigar si existe pérdida de margen" in case.hypothesis # Se usó template
