import pytest
from app.core.orchestrator.service import Orchestrator
from app.core.repositories.hallazgo_repository import MemoryHallazgoRepository

def test_orchestrator_persistence_integration():
    repo = MemoryHallazgoRepository()
    orchestrator = Orchestrator(repository=repo)
    
    source_a = [{"order_id": "O1", "amount": 100}]
    source_b = [{"order_id": "O1", "amount": 110}]
    
    result = orchestrator.run_reconciliation_flow(source_a, source_b)
    
    assert result.success is True
    assert "hallazgos_persistence" in result.steps_executed
    assert len(result.hallazgos) == 1
    
    # Verificar persistencia real en el repositorio
    hallazgo_id = result.hallazgos[0].id
    persisted = repo.get_by_id(hallazgo_id)
    
    assert persisted is not None
    assert persisted.entidad_id == "O1"
    assert persisted.diferencia_cuantificada == 10.0

def test_orchestrator_deduplication_stable_persistence():
    repo = MemoryHallazgoRepository()
    orchestrator = Orchestrator(repository=repo)
    
    source_a = [{"order_id": "O1", "amount": 100}]
    source_b = [{"order_id": "O1", "amount": 110}]
    
    # Primera corrida
    orchestrator.run_reconciliation_flow(source_a, source_b)
    assert len(repo.list_all()) == 1
    
    # Segunda corrida con los mismos datos (mismo dedupe_key -> mismo ID)
    orchestrator.run_reconciliation_flow(source_a, source_b)
    
    # No debe haber duplicados en el repositorio (el ID es estable)
    assert len(repo.list_all()) == 1

def test_orchestrator_reconciliation_to_hallazgos_flow():
    orchestrator = Orchestrator() # Usa MemoryRepo por defecto
    
    source_a = [
        {"order_id": "O1", "amount": 100},
        {"order_id": "O2", "amount": 200}
    ]
    source_b = [
        {"order_id": "O1", "amount": 110},
        {"order_id": "O3", "amount": 300}
    ]
    
    result = orchestrator.run_reconciliation_flow(source_a, source_b)
    
    assert result.success is True
    assert len(result.hallazgos) == 3
    
    # Validar que están en el repositorio interno del orchestrator
    assert len(orchestrator.repository.list_all()) == 3
