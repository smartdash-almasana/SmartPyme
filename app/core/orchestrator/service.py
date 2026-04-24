from typing import Any, Optional
from app.core.orchestrator.models import OrchestrationResult
from app.core.reconciliation.service import reconcile_records
from app.core.hallazgos.service import HallazgoEngine
from app.core.repositories.hallazgo_repository import HallazgoRepository, MemoryHallazgoRepository

class Orchestrator:
    """Orquestador central del flujo de SmartPyme con persistencia integrada."""

    def __init__(self, repository: Optional[HallazgoRepository] = None):
        self.hallazgo_engine = HallazgoEngine()
        self.repository = repository or MemoryHallazgoRepository()

    def run_reconciliation_flow(
        self, 
        source_a: list[dict[str, Any]], 
        source_b: list[dict[str, Any]], 
        key_field: str = "order_id"
    ) -> OrchestrationResult:
        steps = []
        
        try:
            # 1. Reconciliación
            reconciliation_result = reconcile_records(source_a, source_b, key_field)
            steps.append("reconciliation")
            
            # 2. Generación de Hallazgos
            hallazgos = self.hallazgo_engine.transform(reconciliation_result)
            steps.append("hallazgos_generation")
            
            # 3. Persistencia Automática
            for hallazgo in hallazgos:
                self.repository.save(hallazgo)
            steps.append("hallazgos_persistence")
            
            return OrchestrationResult(
                success=True,
                steps_executed=steps,
                reconciliation=reconciliation_result,
                hallazgos=hallazgos
            )
            
        except Exception as e:
            return OrchestrationResult(
                success=False,
                steps_executed=steps,
                errors=[str(e)]
            )
