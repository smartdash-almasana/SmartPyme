from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    success: bool
