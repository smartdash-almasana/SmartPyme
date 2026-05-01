from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RouterContext:
    current_state: str
    flags: dict[str, bool] = field(default_factory=dict)
    last_output: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RoutingDecision:
    status: str
    next_skill_id: str | None
    reason: str
    error_code: str | None
