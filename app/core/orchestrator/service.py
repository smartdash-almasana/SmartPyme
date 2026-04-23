from typing import Any
from app.core.orchestrator.models import OrchestrationResult
from app.core.reconciliation.service import reconcile_records
from app.core.hallazgos.service import HallazgoEngine

class Orchestrator:
    """Orquestador central del flujo de SmartPyme."""

    def __init__(self):
        self.hallazgo_engine = HallazgoEngine()

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
