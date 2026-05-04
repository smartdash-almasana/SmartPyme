from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


DiagnosisStatus = Literal["CONFIRMED", "NOT_CONFIRMED", "INSUFFICIENT_EVIDENCE"]
_ALLOWED_DIAGNOSIS_STATUSES = {"CONFIRMED", "NOT_CONFIRMED", "INSUFFICIENT_EVIDENCE"}


def _require_non_empty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required")


@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    """Capa 03: resultado investigativo; no ejecuta acciones."""

    cliente_id: str
    report_id: str
    case_id: str
    hypothesis: str
    diagnosis_status: DiagnosisStatus
    findings: list[dict[str, Any]] = field(default_factory=list)
    evidence_used: list[str] = field(default_factory=list)
    reasoning_summary: str = ""

    def __post_init__(self) -> None:
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.report_id, "report_id")
        _require_non_empty(self.case_id, "case_id")
        _require_non_empty(self.hypothesis, "hypothesis")
        _require_non_empty(self.reasoning_summary, "reasoning_summary")
        if self.diagnosis_status not in _ALLOWED_DIAGNOSIS_STATUSES:
            raise ValueError(f"invalid diagnosis_status: {self.diagnosis_status}")

    def model_dump(self) -> dict[str, object]:
        return asdict(self)
