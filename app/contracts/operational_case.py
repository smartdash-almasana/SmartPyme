from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


OperationalCaseStatus = Literal["OPEN", "READY_FOR_INVESTIGATION", "BLOCKED", "CLOSED"]
_ALLOWED_STATUSES = {"OPEN", "READY_FOR_INVESTIGATION", "BLOCKED", "CLOSED"}
_INVESTIGATION_PREFIXES = (
    "investigar si",
    "analizar si",
    "determinar si",
    "verificar si",
    "evaluar si",
)


def _require_non_empty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required")


def _require_investigable_hypothesis(value: str) -> None:
    normalized = value.strip().lower()
    if "?" in normalized:
        return
    if any(normalized.startswith(prefix) for prefix in _INVESTIGATION_PREFIXES):
        return
    raise ValueError(
        "HYPOTHESIS_INVALIDA: debe ser una pregunta o empezar con un verbo de investigacion "
        "(Investigar si...)"
    )


@dataclass(frozen=True, slots=True)
class OperationalCase:
    """Capa 03: expediente investigable, no diagnóstico confirmado."""

    cliente_id: str
    case_id: str
    job_id: str
    skill_id: str
    hypothesis: str
    evidence_ids: list[str] = field(default_factory=list)
    status: OperationalCaseStatus = "OPEN"
    symptom_id_orientativo: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.case_id, "case_id")
        _require_non_empty(self.job_id, "job_id")
        _require_non_empty(self.skill_id, "skill_id")
        _require_non_empty(self.hypothesis, "hypothesis")
        _require_investigable_hypothesis(self.hypothesis)
        if self.status not in _ALLOWED_STATUSES:
            raise ValueError(f"invalid operational case status: {self.status}")

    def model_dump(self) -> dict[str, object]:
        return asdict(self)
