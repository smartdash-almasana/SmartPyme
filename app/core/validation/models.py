from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ValidationResult:
    is_valid: bool
    reason: str | None = None
