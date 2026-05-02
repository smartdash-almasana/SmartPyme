import pytest
import sqlite3
from datetime import datetime
from pathlib import Path
from app.contracts.decision_record import DecisionRecord
from app.repositories.decision_repository import DecisionRepository

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_decisions.db"

def test_create_and_get_decision_record(db_path):
    repo = DecisionRepository(cliente_id="C1", db_path=db_path)
    record = DecisionRecord(
        decision_id="D1",
        cliente_id="C1",
        timestamp=datetime.now().isoformat(),
        tipo_decision="EJECUTAR",
        mensaje_original="Confirmar compra",
        propuesta={"item": "prod_1", "monto": 100},
        accion="COMPRAR",
        overrides={"monto": 90},
        job_id="job_123"
    )
    
    repo.create(record)
    fetched = repo.get("D1")
    
    assert fetched == record
    assert fetched.propuesta["monto"] == 100
    assert fetched.overrides["monto"] == 90

def test_list_by_cliente(db_path):
    repo = DecisionRepository(cliente_id="C1", db_path=db_path)
    r1 = DecisionRecord(
        decision_id="D1", cliente_id="C1", timestamp="2026-05-01T12:00:00",
        tipo_decision="INFORMAR", mensaje_original="Hola", propuesta={}, accion="SALUDAR"
    )
    r2 = DecisionRecord(
        decision_id="D2", cliente_id="C1", timestamp="2026-05-01T12:05:00",
        tipo_decision="EJECUTAR", mensaje_original="Ejecutar", propuesta={}, accion="GO"
    )
    
    repo.create(r1)
    repo.create(r2)
    
    decisions = repo.list_by_cliente()
    assert len(decisions) == 2
    ids = [d.decision_id for d in decisions]
    assert "D1" in ids
    assert "D2" in ids

def test_multi_tenant_isolation(db_path):
    repo_c1 = DecisionRepository(cliente_id="C1", db_path=db_path)
    repo_c2 = DecisionRepository(cliente_id="C2", db_path=db_path)
    
    r1 = DecisionRecord(
        decision_id="D1", cliente_id="C1", timestamp="...", 
        tipo_decision="EJECUTAR", mensaje_original="...", propuesta={}, accion="..."
    )
    r2 = DecisionRecord(
        decision_id="D1", cliente_id="C2", timestamp="...", 
        tipo_decision="RECHAZAR", mensaje_original="...", propuesta={}, accion="..."
    )
    
    repo_c1.create(r1)
    repo_c2.create(r2)
    
    # Each repo only sees its own
    assert repo_c1.get("D1").tipo_decision == "EJECUTAR"
    assert repo_c2.get("D1").tipo_decision == "RECHAZAR"
    
    assert len(repo_c1.list_by_cliente()) == 1
    assert len(repo_c2.list_by_cliente()) == 1

def test_violation_of_isolation_raises_error(db_path):
    repo = DecisionRepository(cliente_id="C1", db_path=db_path)
    wrong_record = DecisionRecord(
        decision_id="D1", cliente_id="C2", timestamp="...", 
        tipo_decision="EJECUTAR", mensaje_original="...", propuesta={}, accion="..."
    )
    
    with pytest.raises(ValueError, match="Violacion de aislamiento"):
        repo.create(wrong_record)

def test_none_overrides(db_path):
    repo = DecisionRepository(cliente_id="C1", db_path=db_path)
    record = DecisionRecord(
        decision_id="D1", cliente_id="C1", timestamp="...", 
        tipo_decision="RECHAZAR", mensaje_original="...", propuesta={}, accion="...",
        overrides=None
    )
    
    repo.create(record)
    fetched = repo.get("D1")
    assert fetched.overrides is None
