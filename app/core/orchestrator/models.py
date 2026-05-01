from dataclasses import dataclass, field

from app.core.hallazgos.models import Hallazgo
from app.core.reconciliation.models import ReconciliationResult


@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    success: bool
    steps_executed: list[str] = field(default_factory=list)
    reconciliation: ReconciliationResult | None = None
    hallazgos: list[Hallazgo] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
