from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class PipelineStageResult:
    stage: str
    count: int
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class PipelineCounts:
    facts: int
    canonical: int
    entities: int
    validated_entities: int
    comparison: int
    findings: int
    messages: int = 0
    action_proposals: int = 0


@dataclass(frozen=True, slots=True)
class PipelineResult:
    status: str                          # "OK" | "ERROR" | "BLOCKED"
    job_id: str | None
    plan_id: str | None
    facts: list[Any]
    canonical: list[Any]
    entities: list[Any]
    comparison: list[Any]
    findings: list[Any]
    messages: list[Any]
    action_proposals: list[Any]
    counts: PipelineCounts
    errors: list[str] = field(default_factory=list)
    blocking_reason: str | None = None   # set when status == "BLOCKED"
