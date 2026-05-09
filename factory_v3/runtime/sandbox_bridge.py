from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SandboxExecutionRequest:
    task_id: str
    command: str
    timeout_seconds: int = 60


@dataclass
class SandboxExecutionResult:
    blocked: bool
    returncode: int
    stdout: str
    stderr: str


class SandboxBridge:
    def execute(self, request: SandboxExecutionRequest) -> SandboxExecutionResult:
        return SandboxExecutionResult(
            blocked=True,
            returncode=-1,
            stdout="",
            stderr="sandbox adapter not connected",
        )
