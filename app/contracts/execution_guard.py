from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_BLOCKING_STATUSES = {
    "BLOCKED",
    "NEEDS_EVIDENCE",
    "MISSING_CONTRACT",
    "BLOCKED_MISSING_CONTRACT",
    "BLOCKED_MISSING_VARIABLES",
}
_BLOCKING_FIELDS = ("status", "current_state", "state")
_REASON_FIELDS = ("blocking_reason", "blocked_reason")


def _read_field(contract: object, field_name: str) -> Any:
    if isinstance(contract, Mapping):
        return contract.get(field_name)
    return getattr(contract, field_name, None)


def _status_value(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip().upper()


def _has_blocking_reason(contract: object) -> bool:
    return any(bool(_read_field(contract, field_name)) for field_name in _REASON_FIELDS)


def _validate_nested_payload(contract: object, *, context: str) -> None:
    if not isinstance(contract, Mapping):
        return

    payload = contract.get("payload")
    if payload is not None and not isinstance(payload, Mapping):
        raise ValueError(
            f"EXECUTION_BLOCKED[{context}]: payload must be a mapping before execution"
        )

    for nested_name in ("payload", "operational_plan"):
        nested = contract.get(nested_name)
        if not isinstance(nested, Mapping):
            continue
        enforce_execution_contract(
            nested,
            context=f"{context}.{nested_name}",
            required_fields=(),
            allow_statusless=True,
        )

    if isinstance(payload, Mapping):
        operational_plan = payload.get("operational_plan")
        if isinstance(operational_plan, Mapping):
            enforce_execution_contract(
                operational_plan,
                context=f"{context}.payload.operational_plan",
                required_fields=(),
                allow_statusless=True,
            )


def enforce_execution_contract(
    contract: object,
    *,
    context: str,
    required_fields: tuple[str, ...] = (),
    allow_statusless: bool = True,
) -> None:
    """Fail closed before a job/case can trigger persistence or side effects.

    This guard intentionally does not introduce a new model hierarchy. It accepts
    the existing dict/dataclass/Pydantic-like contracts used across the runtime
    and blocks execution when the input is absent, explicitly blocked, awaiting
    evidence, internally inconsistent, or missing caller-declared required fields.
    """

    if contract is None:
        raise ValueError(f"EXECUTION_BLOCKED[{context}]: missing execution contract")

    if not context or not context.strip():
        raise ValueError("EXECUTION_BLOCKED[unknown]: context is required")

    missing_fields = [
        field_name
        for field_name in required_fields
        if _read_field(contract, field_name) in (None, "")
    ]
    if missing_fields:
        raise ValueError(
            f"EXECUTION_BLOCKED[{context}]: missing required fields: "
            + ", ".join(missing_fields)
        )

    observed_statuses: list[str] = []
    for field_name in _BLOCKING_FIELDS:
        status = _status_value(_read_field(contract, field_name))
        if status:
            observed_statuses.append(status)
        if status in _BLOCKING_STATUSES:
            raise ValueError(
                f"EXECUTION_BLOCKED[{context}]: contract is not executable "
                f"({field_name}={status})"
            )

    if not allow_statusless and not observed_statuses:
        raise ValueError(f"EXECUTION_BLOCKED[{context}]: missing execution status")

    if _has_blocking_reason(contract) and not any(
        status in _BLOCKING_STATUSES for status in observed_statuses
    ):
        raise ValueError(
            f"EXECUTION_BLOCKED[{context}]: blocking_reason present without blocking status"
        )

    _validate_nested_payload(contract, context=context)
