from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    AUDITOR = "auditor"


class TaskState(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"
    FAILED = "failed"


class ArtifactType(str, Enum):
    PLAN = "plan"
    CODE_PATCH = "code_patch"
    TEST_REPORT = "test_report"
    APPROVAL_TOKEN = "approval_token"


class AgentCard(BaseModel):
    agent_id: str
    capabilities: List[str] = Field(default_factory=list)
    role: AgentRole


class TaskEnvelope(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    objective: str
    status: TaskState = TaskState.PENDING
    assigned_agent: str
    dependencies: List[str] = Field(default_factory=list)


class ArtifactEnvelope(BaseModel):
    artifact_id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    artifact_type: ArtifactType
    storage_path: str
    content_hash: str
    producer_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    parent_artifacts: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    def absolute_path(self) -> Path:
        return Path(self.storage_path)

    def exists(self) -> bool:
        return self.absolute_path().exists()

    def read_content(self) -> str:
        return self.absolute_path().read_text(encoding="utf-8")
