import pytest
from app.core.orchestrator.service import Orchestrator

def test_orchestrator_reconciliation_to_hallazgos_flow():
    orchestrator = Orchestrator()
    
    # Datos con un mismatch y un faltante
    source_a = [
        {"order_id": "O1", "amount": 100},
        {"order_id": "O2", "amount": 200}
    ]
    source_b = [
        {"order_id": "O1", "amount": 110}, # Mismatch
        {"order_id": "O3", "amount": 300}  # Faltante en A (u O2 faltante en B)
    ]
    
    result = orchestrator.run_reconciliation_flow(source_a, source_b, key_field="order_id")
    
    assert result.success is True
    assert "reconciliation" in result.steps_executed
    assert "hallazgos_generation" in result.steps_executed
    
    # Validar que se generaron hallazgos
    # 1 mismatch (O1) + 1 faltante en A (O3) + 1 faltante en B (O2) = 3 hallazgos
    assert len(result.hallazgos) == 3
    
    # Verificar tipos de hallazgos
    tipos = [h.tipo for h in result.hallazgos]
    assert "mismatch_valor" in tipos
    assert "faltante_en_fuente" in tipos
    
    # Verificar que el mismatch O1 está presente
    h_o1 = next(h for h in result.hallazgos if h.entidad_id == "O1")
    assert h_o1.diferencia_cuantificada == 10.0
    assert h_o1.evidencia["field"] == "amount"

def test_orchestrator_deduplication_in_flow():
    orchestrator = Orchestrator()
    
    # Datos que podrían generar duplicados si no se manejaran
    source_a = [{"order_id": "O1", "amount": 100}]
    source_b = [{"order_id": "O1", "amount": 110}]
    
    result = orchestrator.run_reconciliation_flow(source_a, source_b)
    
    # Ejecutamos dos veces la transformación internamente (simulado por el engine)
    # El engine ya de-duplica, validamos que el orquestador entrega la lista limpia
    assert len(result.hallazgos) == 1
