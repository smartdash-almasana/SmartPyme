from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DirectorRequest:
    objetivo: str
    payload_inicial: dict[str, Any] = field(default_factory=dict)
    flags: dict[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class DirectorPlan:
    status: str
    objetivo: str
    initial_state: str
    initial_payload: dict[str, Any]
    flags: dict[str, bool]
    error_code: str | None
    error_message: str | None
