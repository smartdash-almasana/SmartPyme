from app.core.hallazgos.models import Hallazgo
from app.core.hallazgos.service import HallazgoEngine, HallazgoService
from app.core.reconciliation.models import QuantifiedDiscrepancy, ReconciliationResult
from app.core.repositories.hallazgo_repository import MemoryHallazgoRepository


def test_hallazgo_service_query_and_summary():
    repo = MemoryHallazgoRepository()
    service = HallazgoService(repo)
    
    # Setup datos de prueba
    h1 = Hallazgo(
        id="h1", tipo="mismatch_valor", severidad="critical", entidad_id="e1", 
        entidad_tipo="order", diferencia_cuantificada=600, evidencia={}, 
        dedupe_key="d1", status="pending"
    )
    h2 = Hallazgo(
        id="h2", tipo="mismatch_valor", severidad="warning", entidad_id="e2", 
        entidad_tipo="order", diferencia_cuantificada=10, evidencia={}, 
        dedupe_key="d2", status="done"
    )
    repo.save(h1)
    repo.save(h2)
    
    # Test filtrado via servicio
    pending = service.get_findings(status="pending")
    assert len(pending) == 1
    assert pending[0].id == "h1"
    
    # Test resumen
    summary = service.get_summary()
    assert summary["total"] == 2
    assert summary["by_status"]["pending"] == 1
    assert summary["by_status"]["done"] == 1
    assert summary["by_severity"]["critical"] == 1
    assert summary["critical_pending"] == 1

def test_hallazgo_service_status_lifecycle():
    repo = MemoryHallazgoRepository()
    service = HallazgoService(repo)
    
    h = Hallazgo(
        id="h1", tipo="mismatch_valor", severidad="warning", entidad_id="e1", 
        entidad_tipo="order", diferencia_cuantificada=10, evidencia={}, 
        dedupe_key="d1", status="pending"
    )
    repo.save(h)
    
    # Actualizar a in_progress
    updated = service.update_status("h1", "in_progress")
    assert updated.status == "in_progress"
    assert repo.get_by_id("h1").status == "in_progress"
    
    # Hallazgo inexistente
    assert service.update_status("invalid", "done") is None

def test_hallazgo_engine_full_logic():
    # Mantener tests anteriores del engine
    engine = HallazgoEngine()
    m = QuantifiedDiscrepancy("k", "f", 1, 2, -1.0, "mismatch_numerico")
    result = ReconciliationResult([], [m], [], [])
    hallazgos = engine.transform(result)
    assert len(hallazgos) == 1
    assert hallazgos[0].severidad == "warning"
