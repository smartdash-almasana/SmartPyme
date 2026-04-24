import pytest
from app.core.hallazgos.models import Hallazgo
from app.core.repositories.hallazgo_repository import MemoryHallazgoRepository

def test_memory_repository_filtering():
    repo = MemoryHallazgoRepository()
    
    # Hallazgo 1: pending, warning, mismatch
    h1 = Hallazgo(
        id="h1", tipo="mismatch_valor", severidad="warning", entidad_id="e1", 
        entidad_tipo="order", diferencia_cuantificada=10, evidencia={}, 
        dedupe_key="d1", status="pending"
    )
    # Hallazgo 2: done, critical, mismatch
    h2 = Hallazgo(
        id="h2", tipo="mismatch_valor", severidad="critical", entidad_id="e2", 
        entidad_tipo="order", diferencia_cuantificada=1000, evidencia={}, 
        dedupe_key="d2", status="done"
    )
    # Hallazgo 3: pending, critical, faltante
    h3 = Hallazgo(
        id="h3", tipo="faltante_en_fuente", severidad="critical", entidad_id="e3", 
        entidad_tipo="order", diferencia_cuantificada="miss", evidencia={}, 
        dedupe_key="d3", status="pending"
    )
    
    for h in [h1, h2, h3]:
        repo.save(h)
    
    # 1. Sin filtros
    assert len(repo.list_all()) == 3
    
    # 2. Por Status
    assert len(repo.list_all(status="pending")) == 2
    assert len(repo.list_all(status="done")) == 1
    
    # 3. Por Severidad
    assert len(repo.list_all(severity="critical")) == 2
    assert len(repo.list_all(severity="warning")) == 1
    
    # 4. Por Tipo
    assert len(repo.list_all(tipo="faltante_en_fuente")) == 1
    
    # 5. Combinado (pending + critical)
    result = repo.list_all(status="pending", severity="critical")
    assert len(result) == 1
    assert result[0].id == "h3"

def test_memory_repository_empty_filters():
    repo = MemoryHallazgoRepository()
    assert len(repo.list_all(severity="critical")) == 0
    assert len(repo.list_all(tipo="incertidumbre")) == 0
