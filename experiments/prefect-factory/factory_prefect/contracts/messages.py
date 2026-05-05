from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class AgentRole(StrEnum):
    ARCHITECT = "ARCHITECT"
    PLANNER = "PLANNER"
    CODER = "CODER"
    REVIEWER = "REVIEWER"
    HERMES_GATEWAY = "HERMES_GATEWAY"
    SANDBOX = "SANDBOX"
    PUBLISHER = "PUBLISHER"


class FactoryStatus(StrEnum):
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"
    DONE = "DONE"
    FAILED = "FAILED"


class CodePatchProposal(BaseModel):
    task_id: str
    summary: str
    files_to_create: dict[str, str] = Field(default_factory=dict)
    files_to_modify: dict[str, str] = Field(default_factory=dict)
    tests_to_run: list[str] = Field(default_factory=list)
    requires_sandbox_execution: bool = True
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"

    @model_validator(mode="after")
    def must_have_change(self) -> "CodePatchProposal":
        if not self.files_to_create and not self.files_to_modify:
            raise ValueError("Patch proposal must create or modify at least one file")
        return self


class ReviewDecision(BaseModel):
    task_id: str
    decision: Literal["PASS", "BLOCKED", "HUMAN_REQUIRED"]
    reasons: list[str] = Field(default_factory=list)
    commands_to_validate: list[str] = Field(default_factory=list)
    dangerous_commands_detected: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def dangerous_requires_human(self) -> "ReviewDecision":
        if self.dangerous_commands_detected and self.decision != "HUMAN_REQUIRED":
            raise ValueError("Dangerous commands must produce HUMAN_REQUIRED")
        return self


class FactoryEvent(BaseModel):
    event_id: str
    run_id: str
    source: AgentRole
    target: AgentRole | None = None
    event_type: str
    payload: dict
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
