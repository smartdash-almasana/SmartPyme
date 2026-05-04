from __future__ import annotations

from dataclasses import asdict, dataclass


def _require_non_empty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required")


@dataclass(frozen=True, slots=True)
class ActionProposal:
    """Capa 03: propuesta posterior al reporte; no es decisión ni autorización."""

    cliente_id: str
    proposal_id: str
    report_id: str
    recommended_action: str
    rationale: str
    requires_owner_decision: bool = True

    def __post_init__(self) -> None:
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.proposal_id, "proposal_id")
        _require_non_empty(self.report_id, "report_id")
        _require_non_empty(self.recommended_action, "recommended_action")
        _require_non_empty(self.rationale, "rationale")
        if not self.requires_owner_decision:
            raise ValueError("ActionProposal requires owner decision")

    def model_dump(self) -> dict[str, object]:
        return asdict(self)
