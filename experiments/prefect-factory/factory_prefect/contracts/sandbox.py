from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class SandboxExecutionRequest(BaseModel):
    task_id: str
    command: str
    cwd: str = "."
    timeout_seconds: int = 120
    network_disabled: bool = True

    @model_validator(mode="after")
    def validate_request(self) -> "SandboxExecutionRequest":
        if not self.command.strip():
            raise ValueError("command is required")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        return self


class SandboxExecutionResult(BaseModel):
    task_id: str
    command: str
    returncode: int
    stdout: str
    stderr: str
    blocked: bool = False
    requires_human_approval: bool = False
    reasons: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_blocked_result(self) -> "SandboxExecutionResult":
        if self.requires_human_approval and not self.blocked:
            raise ValueError("human approval requirement must block execution")
        if self.blocked and not self.reasons:
            raise ValueError("blocked execution requires reasons")
        return self
