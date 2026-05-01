from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SkillSpec:
    skill_id: str
    name: str
    version: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    validator_ref: str | None
    executor_ref: str
    accuracy_score: float
    enabled: bool
