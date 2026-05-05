from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from factory_prefect.contracts.messages import AgentRole, FactoryStatus


class LedgerTask(BaseModel):
    task_id: str
    objective: str
    assigned_role: AgentRole
    status: FactoryStatus = FactoryStatus.READY
    allowed_paths: list[str] = Field(default_factory=list)
    forbidden_paths: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    validation_commands: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class TaskLedger(BaseModel):
    run_id: str
    root_objective: str
    tasks: list[LedgerTask]
    facts: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProgressEntry(BaseModel):
    step_id: str
    task_id: str
    agent: AgentRole
    status: FactoryStatus
    summary: str
    details: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProgressLedger(BaseModel):
    run_id: str
    entries: list[ProgressEntry] = Field(default_factory=list)

    def append(self, entry: ProgressEntry) -> None:
        self.entries.append(entry)
