from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentLoopContext:
    current_state: str
    flags: dict[str, bool] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)
    last_output: dict[str, Any] = field(default_factory=dict)
    executed_skills: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AgentLoopResult:
    status: str
    executed_skills: list[str]
    final_state: str
    final_output: dict[str, Any] | None
    error_code: str | None
    error_message: str | None
