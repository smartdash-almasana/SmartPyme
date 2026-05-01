from dataclasses import dataclass, field
from typing import Any

STATE_CREATED = "CREATED"
STATE_RUNNING = "RUNNING"
STATE_COMPLETED = "COMPLETED"
STATE_BLOCKED = "BLOCKED"


@dataclass
class Job:
    job_id: str
    current_state: str = STATE_CREATED
    status: str = "created"
    skill_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] | None = None
    blocking_reason: str | None = None
    error_code: str | None = None
