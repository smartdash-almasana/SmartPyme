from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ALLOWED_BEM_RUN_STATUS = {"SUBMITTED", "COMPLETED", "FAILED"}


def _require_non_empty_str(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")


def _require_non_empty_dict(value: dict[str, Any], field_name: str) -> None:
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{field_name} is required")


@dataclass(slots=True)
class BemRunRecord:
    tenant_id: str
    run_id: str
    workflow_id: str
    status: str
    request_payload: dict[str, Any]
    response_payload: dict[str, Any] | None
    created_at: str
    updated_at: str | None
    error_message: str | None

    def __post_init__(self) -> None:
        _require_non_empty_str(self.tenant_id, "tenant_id")
        _require_non_empty_str(self.run_id, "run_id")
        _require_non_empty_str(self.workflow_id, "workflow_id")
        _require_non_empty_str(self.created_at, "created_at")
        _require_non_empty_dict(self.request_payload, "request_payload")
        if self.status not in ALLOWED_BEM_RUN_STATUS:
            raise ValueError("status is invalid")
        if self.response_payload is not None and not isinstance(self.response_payload, dict):
            raise TypeError("response_payload must be dict or None")
        if self.updated_at is not None and not isinstance(self.updated_at, str):
            raise TypeError("updated_at must be str or None")
        if self.error_message is not None and not isinstance(self.error_message, str):
            raise TypeError("error_message must be str or None")
