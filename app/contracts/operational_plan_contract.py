from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class OperationalPlanContract:
    plan_id: str
    cliente_id: str
    owner_request: str
    objective: str
    period: dict[str, Any] | None
    operational_vectors: list[str] = field(default_factory=list)
    required_sources: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    status: str = "draft"


def _require_non_empty_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name.upper()}_INVALIDO: debe ser texto no vacio.")
    return value.strip()


def _validate_text_list(values: list[str], field_name: str) -> list[str]:
    if not isinstance(values, list):
        raise ValueError(f"{field_name.upper()}_INVALIDO: debe ser una lista.")

    cleaned: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field_name.upper()}_INVALIDO: item {index} debe ser texto no vacio."
            )
        cleaned.append(value.strip())

    return cleaned


def create_operational_plan(
    *,
    cliente_id: str,
    owner_request: str,
    objective: str,
    period: dict[str, Any] | None = None,
    operational_vectors: list[str] | None = None,
    required_sources: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
    plan_id: str | None = None,
    status: str = "draft",
) -> OperationalPlanContract:
    if period is not None and not isinstance(period, dict):
        raise ValueError("PERIOD_INVALIDO: debe ser object o null.")

    return OperationalPlanContract(
        plan_id=_require_non_empty_text(plan_id, "plan_id")
        if plan_id is not None
        else f"plan-{uuid.uuid4().hex[:12]}",
        cliente_id=_require_non_empty_text(cliente_id, "cliente_id"),
        owner_request=_require_non_empty_text(owner_request, "owner_request"),
        objective=_require_non_empty_text(objective, "objective"),
        period=period,
        operational_vectors=_validate_text_list(
            operational_vectors or [], "operational_vectors"
        ),
        required_sources=_validate_text_list(required_sources or [], "required_sources"),
        acceptance_criteria=_validate_text_list(
            acceptance_criteria or [], "acceptance_criteria"
        ),
        status=_require_non_empty_text(status, "status"),
    )
