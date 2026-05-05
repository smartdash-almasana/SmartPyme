from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class HumanApprovalRequest(BaseModel):
    run_id: str
    task_id: str
    risk_type: Literal[
        "INFRASTRUCTURE_CHANGE",
        "DANGEROUS_COMMAND",
        "PYDANTIC_VALIDATION_FAILURE",
        "SANDBOX_EXECUTION",
        "GIT_PUBLICATION",
        "MANUAL_DECISION",
    ]
    question: str
    context_summary: str
    command: str | None = None
    options: list[str] = Field(default_factory=lambda: ["APPROVE", "REJECT"])
    idempotency_key: str
    timeout_seconds: int = 86400
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_request(self) -> "HumanApprovalRequest":
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if not self.idempotency_key.strip():
            raise ValueError("idempotency_key is required")
        if self.risk_type == "DANGEROUS_COMMAND" and not self.command:
            raise ValueError("command is required for DANGEROUS_COMMAND approval")
        return self


class HumanApprovalResult(BaseModel):
    ticket_id: str
    status: Literal["RESOLVED", "TIMEOUT", "FAILED", "CANCELLED"]
    approved: bool
    decision_type: Literal["APPROVE", "REJECT", "REQUEST_CHANGES", "TIMEOUT", "FAILED"]
    raw_message: str | None = None
    normalized_answer: dict = Field(default_factory=dict)
    resolved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_fail_closed(self) -> "HumanApprovalResult":
        if self.status != "RESOLVED" and self.approved:
            raise ValueError("non-RESOLVED results must not be approved")
        if self.decision_type != "APPROVE" and self.approved:
            raise ValueError("only APPROVE decisions can be approved")
        if self.decision_type == "APPROVE" and not self.approved:
            raise ValueError("APPROVE decision requires approved=true")
        return self
