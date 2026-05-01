from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChainStep:
    step_id: str
    skill_id: str


@dataclass(frozen=True)
class ChainExecutionResult:
    status: str
    completed_steps: list[str]
    final_output: dict[str, Any] | None
    failed_step_id: str | None
    error_code: str | None
    error_message: str | None
