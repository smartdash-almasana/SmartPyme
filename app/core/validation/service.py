from app.core.validation.models import ValidationResult

def validate_data(data: dict) -> ValidationResult:
    if not data:
        return ValidationResult(is_valid=False, reason="Data is empty")
    return ValidationResult(is_valid=True)
